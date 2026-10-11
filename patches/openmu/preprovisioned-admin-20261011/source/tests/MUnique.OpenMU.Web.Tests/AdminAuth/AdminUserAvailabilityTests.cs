// <copyright file="AdminUserAvailabilityTests.cs" company="MUnique">
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// </copyright>

namespace MUnique.OpenMU.Web.Tests.AdminAuth;

using System.Threading;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Moq;
using MUnique.OpenMU.Persistence.AdminAuth;
using MUnique.OpenMU.Web.AdminPanel.Auth;

/// <summary>
/// Bounded, database-free regressions for the real availability service.
/// </summary>
[TestFixture]
public class AdminUserAvailabilityTests
{
    private static readonly TimeSpan TestTimeout = TimeSpan.FromSeconds(5);

    /// <summary>
    /// Concurrent first checks wait and share only the completed result.
    /// </summary>
    /// <param name="count">The number of users returned by storage.</param>
    [TestCase(0)]
    [TestCase(1)]
    public async Task ConcurrentFirstChecksWaitAndCacheAsync(int count)
    {
        var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var repository = CreateRepository(count);
        repository.Setup(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()))
            .Returns((CancellationToken token) => new ValueTask<bool>(release.Task.WaitAsync(token)));
        var service = CreateService(repository.Object);
        var first = service.AnyUserExistsAsync().AsTask();
        var second = service.AnyUserExistsAsync().AsTask();
        try
        {
            Assert.That(first.IsCompleted, Is.False);
            Assert.That(second.IsCompleted, Is.False);
        }
        finally
        {
            release.TrySetResult(true);
        }

        Assert.That(await first.WaitAsync(TestTimeout).ConfigureAwait(false), Is.EqualTo(count > 0));
        Assert.That(await second.WaitAsync(TestTimeout).ConfigureAwait(false), Is.EqualTo(count > 0));
        Assert.That(await service.AnyUserExistsAsync().ConfigureAwait(false), Is.EqualTo(count > 0));
        repository.Verify(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()), Times.Once);
        repository.Verify(r => r.GetCountAsync(It.IsAny<CancellationToken>()), Times.Once);
    }

    /// <summary>
    /// External storage or count errors never become a cached false answer.
    /// </summary>
    /// <param name="failCount">Whether the failure is in counting rather than validation.</param>
    [TestCase(false)]
    [TestCase(true)]
    public async Task FailedCheckPropagatesAndNextCallRetriesAsync(bool failCount)
    {
        var repository = CreateRepository(1);
        var failure = new InvalidOperationException("External storage validation failed.");
        if (failCount)
        {
            repository.SetupSequence(r => r.GetCountAsync(It.IsAny<CancellationToken>()))
                .Throws(failure).Returns(ValueTask.FromResult(1));
        }
        else
        {
            repository.SetupSequence(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()))
                .Throws(failure).Returns(ValueTask.FromResult(true));
        }

        var service = CreateService(repository.Object);
        var error = Assert.ThrowsAsync<InvalidOperationException>(async () =>
        {
            await service.AnyUserExistsAsync().AsTask().WaitAsync(TestTimeout).ConfigureAwait(false);
        });
        Assert.That(error, Is.SameAs(failure));
        Assert.That(await service.AnyUserExistsAsync().AsTask().WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
        repository.Verify(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()), Times.Exactly(2));
    }

    /// <summary>
    /// Cancelling a waiting caller neither cancels the owner nor adds a semaphore permit.
    /// </summary>
    [Test]
    public async Task CancelledWaiterLeavesOwnerAndSemaphoreIntactAsync()
    {
        var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var repository = CreateRepository(1);
        repository.Setup(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()))
            .Returns((CancellationToken token) => new ValueTask<bool>(release.Task.WaitAsync(token)));
        var service = CreateService(repository.Object);
        var owner = service.AnyUserExistsAsync().AsTask();
        using var cancellation = new CancellationTokenSource();
        var waiter = service.AnyUserExistsAsync(cancellation.Token).AsTask();
        cancellation.Cancel();
        Assert.CatchAsync<OperationCanceledException>(async () => await waiter.WaitAsync(TestTimeout).ConfigureAwait(false));
        var remainingWaiter = service.AnyUserExistsAsync().AsTask();
        Assert.That(owner.IsCompleted, Is.False);
        Assert.That(remainingWaiter.IsCompleted, Is.False);
        repository.Verify(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()), Times.Once);
        release.TrySetResult(true);
        Assert.That(await owner.WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
        Assert.That(await remainingWaiter.WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
    }

    /// <summary>
    /// An owner cancellation releases the semaphore without caching an incomplete answer.
    /// </summary>
    [Test]
    public async Task CancelledOwnerAllowsFreshWaitingCheckAsync()
    {
        var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var repository = CreateRepository(1);
        var probes = 0;
        repository.Setup(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()))
            .Returns((CancellationToken token) => Interlocked.Increment(ref probes) == 1
                ? new ValueTask<bool>(release.Task.WaitAsync(token))
                : ValueTask.FromResult(true));
        var service = CreateService(repository.Object);
        using var cancellation = new CancellationTokenSource();
        var owner = service.AnyUserExistsAsync(cancellation.Token).AsTask();
        var waiter = service.AnyUserExistsAsync().AsTask();
        cancellation.Cancel();
        Assert.CatchAsync<OperationCanceledException>(async () => await owner.WaitAsync(TestTimeout).ConfigureAwait(false));
        Assert.That(await waiter.WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
        Assert.That(probes, Is.EqualTo(2));
        repository.Verify(r => r.GetCountAsync(It.IsAny<CancellationToken>()), Times.Once);
    }

    /// <summary>
    /// Even a repository which ignores cancellation cannot publish its stale false result.
    /// </summary>
    [Test]
    public async Task CancellationAfterRepositoryCompletionIsNotCachedAsync()
    {
        var release = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);
        var repository = CreateRepository(0);
        repository.SetupSequence(r => r.GetCountAsync(It.IsAny<CancellationToken>()))
            .Returns(new ValueTask<int>(release.Task)).Returns(ValueTask.FromResult(1));
        var service = CreateService(repository.Object);
        using var cancellation = new CancellationTokenSource();
        var owner = service.AnyUserExistsAsync(cancellation.Token).AsTask();
        cancellation.Cancel();
        release.TrySetResult(0);
        Assert.CatchAsync<OperationCanceledException>(async () => await owner.WaitAsync(TestTimeout).ConfigureAwait(false));
        Assert.That(await service.AnyUserExistsAsync().AsTask().WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
    }

    /// <summary>
    /// Invalidation during an old check fails closed and requires a new count.
    /// </summary>
    /// <param name="firstCount">The stale result.</param>
    [TestCase(0)]
    [TestCase(1)]
    public async Task InvalidationDuringCheckRequiresFreshProbeAsync(int firstCount)
    {
        var release = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);
        var repository = CreateRepository(0);
        repository.SetupSequence(r => r.GetCountAsync(It.IsAny<CancellationToken>()))
            .Returns(new ValueTask<int>(release.Task)).Returns(ValueTask.FromResult(0));
        var service = CreateService(repository.Object);
        var owner = service.AnyUserExistsAsync().AsTask();
        service.Invalidate();
        release.TrySetResult(firstCount);
        Assert.That(await owner.WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
        Assert.That(await service.AnyUserExistsAsync().ConfigureAwait(false), Is.False);
        repository.Verify(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>()), Times.Exactly(2));
        repository.Verify(r => r.GetCountAsync(It.IsAny<CancellationToken>()), Times.Exactly(2));
    }

    /// <summary>
    /// Explicit invalidation refreshes both a cached positive and a cached zero answer.
    /// </summary>
    /// <param name="initialCount">The first count.</param>
    [TestCase(0)]
    [TestCase(1)]
    public async Task InvalidationRefreshesCompletedCacheAsync(int initialCount)
    {
        var repository = CreateRepository(initialCount);
        repository.SetupSequence(r => r.GetCountAsync(It.IsAny<CancellationToken>()))
            .Returns(ValueTask.FromResult(initialCount)).Returns(ValueTask.FromResult(1 - initialCount));
        var service = CreateService(repository.Object);
        Assert.That(await service.AnyUserExistsAsync().ConfigureAwait(false), Is.EqualTo(initialCount > 0));
        service.Invalidate();
        Assert.That(await service.AnyUserExistsAsync().ConfigureAwait(false), Is.EqualTo(initialCount == 0));
        repository.Verify(r => r.GetCountAsync(It.IsAny<CancellationToken>()), Times.Exactly(2));
    }

    private static Mock<IAdminUserRepository> CreateRepository(int count)
    {
        var repository = new Mock<IAdminUserRepository>(MockBehavior.Strict);
        repository.Setup(r => r.EnsureStorageAsync(It.IsAny<CancellationToken>())).Returns(ValueTask.FromResult(true));
        repository.Setup(r => r.GetCountAsync(It.IsAny<CancellationToken>())).Returns(ValueTask.FromResult(count));
        return repository;
    }

    private static AdminUserAvailabilityService CreateService(IAdminUserRepository repository)
    {
        var bootstrap = new BootstrapAdminUserProvider(
            Options.Create(new AdminPanelAuthOptions()),
            Mock.Of<IPasswordHasher<AdminUser>>(),
            new AdminUserSecretProtector(new EphemeralDataProtectionProvider(), NullLogger<AdminUserSecretProtector>.Instance),
            NullLogger<BootstrapAdminUserProvider>.Instance);
        return new AdminUserAvailabilityService(repository, bootstrap);
    }
}

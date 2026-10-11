// <copyright file="AdminUserRepositoryStorageTests.cs" company="MUnique">
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// </copyright>

namespace MUnique.OpenMU.Tests;

using System.Reflection;
using System.Threading;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;
using Microsoft.EntityFrameworkCore.Storage;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using MUnique.OpenMU.Persistence;
using MUnique.OpenMU.Persistence.EntityFramework;
using MUnique.OpenMU.Persistence.EntityFramework.AdminAuth;

/// <summary>
/// Exercises the repository's real external-storage branch without configuring a database provider.
/// </summary>
[TestFixture]
public class AdminUserRepositoryStorageTests
{
    private static readonly TimeSpan TestTimeout = TimeSpan.FromSeconds(5);

    private Mock<AdminPanelContext> _context = null!;
    private Mock<DatabaseFacade> _database = null!;
    private Mock<IHistoryRepository> _history = null!;
    private Mock<IMigrationsAssembly> _migrations = null!;
    private Mock<IMigrator> _migrator = null!;
    private Mock<IDatabaseCreator> _creator = null!;
    private AdminUserRepository _repository = null!;
    private int _contextCreations;

    /// <summary>
    /// Configures only EF read services. All unconfigured service and DDL calls throw.
    /// </summary>
    [SetUp]
    public void SetUp()
    {
        this._contextCreations = 0;
        this._context = new Mock<AdminPanelContext>(MockBehavior.Strict);
        this._history = new Mock<IHistoryRepository>(MockBehavior.Strict);
        this._migrations = new Mock<IMigrationsAssembly>(MockBehavior.Strict);
        this._migrator = new Mock<IMigrator>(MockBehavior.Strict);
        this._creator = new Mock<IDatabaseCreator>(MockBehavior.Strict);
        var services = new Mock<IServiceProvider>(MockBehavior.Strict);
        services.Setup(s => s.GetService(typeof(IHistoryRepository))).Returns(this._history.Object);
        services.Setup(s => s.GetService(typeof(IMigrationsAssembly))).Returns(this._migrations.Object);
        services.Setup(s => s.GetService(typeof(IMigrator))).Returns(this._migrator.Object);
        services.Setup(s => s.GetService(typeof(IDatabaseCreator))).Returns(this._creator.Object);

        this._database = new Mock<DatabaseFacade>(MockBehavior.Strict, this._context.Object);
        this._database.As<IInfrastructure<IServiceProvider>>().SetupGet(d => d.Instance).Returns(services.Object);
        this._database.Setup(d => d.CanConnectAsync(It.IsAny<CancellationToken>())).ReturnsAsync(true);
        this._context.SetupGet(c => c.Database).Returns(this._database.Object);
        this._context.Setup(c => c.DisposeAsync()).Returns(ValueTask.CompletedTask);
        this.SetHistory("A,B", "A,B");

        // Only SetupService's event subscription is used; no initialization method is invoked.
        var setupService = new SetupService(Mock.Of<IMigratableDatabaseContextProvider>(), null!);
        this._repository = new AdminUserRepository(
            setupService,
            NullLogger<AdminUserRepository>.Instance,
            () =>
            {
                this._contextCreations++;
                return this._context.Object;
            },
            () => ValueTask.FromResult(AdminSchemaManagementMode.ExternallyProvisioned));
    }

    /// <summary>
    /// Verifies every case remained read-only and releases event subscriptions.
    /// </summary>
    [TearDown]
    public void TearDown()
    {
        this._repository.Dispose();
        this._migrator.VerifyNoOtherCalls();
        this._creator.VerifyNoOtherCalls();
        this._database.Verify(d => d.EnsureCreated(), Times.Never);
        this._database.Verify(d => d.EnsureCreatedAsync(It.IsAny<CancellationToken>()), Times.Never);
        this._database.Verify(d => d.EnsureDeleted(), Times.Never);
        this._database.Verify(d => d.EnsureDeletedAsync(It.IsAny<CancellationToken>()), Times.Never);
        this._history.Verify(h => h.Create(), Times.Never);
        this._history.Verify(h => h.CreateAsync(It.IsAny<CancellationToken>()), Times.Never);
        this._history.Verify(h => h.AcquireDatabaseLock(), Times.Never);
        this._history.Verify(h => h.AcquireDatabaseLockAsync(It.IsAny<CancellationToken>()), Times.Never);
    }

    /// <summary>
    /// Exact histories, including differently ordered reads, validate once and are cached.
    /// </summary>
    /// <param name="applied">The applied IDs.</param>
    [TestCase("A,B")]
    [TestCase("B,A")]
    public async Task MatchingHistoryIsReadOnlyAndCachedAsync(string applied)
    {
        this.SetHistory("A,B", applied);
        Assert.That(await this.CheckAsync().ConfigureAwait(false), Is.True);
        Assert.That(await this.CheckAsync().ConfigureAwait(false), Is.True);
        Assert.That(this._contextCreations, Is.EqualTo(1));
        this._database.Verify(d => d.CanConnectAsync(It.IsAny<CancellationToken>()), Times.Once);
        this._history.Verify(h => h.GetAppliedMigrationsAsync(It.IsAny<CancellationToken>()), Times.Once);
        this._context.Verify(c => c.DisposeAsync(), Times.Once);
    }

    /// <summary>
    /// Missing, extra, wrong, duplicated, or empty compiled histories fail closed.
    /// </summary>
    /// <param name="expected">The compiled IDs.</param>
    /// <param name="applied">The applied IDs.</param>
    [TestCase("A,B", "")]
    [TestCase("A,B", "A")]
    [TestCase("A,B", "A,B,C")]
    [TestCase("A,B", "A,C")]
    [TestCase("A,B", "A,A,B")]
    [TestCase("A,B", "A,A")]
    [TestCase("", "")]
    public void MismatchedHistoryThrowsAndBacksOff(string expected, string applied)
    {
        this.SetHistory(expected, applied);
        var error = Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(error!.Message, Does.Contain("migration history does not match"));
        var retry = Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(retry!.Message, Does.Contain("probe delay"));
        Assert.That(this._contextCreations, Is.EqualTo(1));
        this._context.Verify(c => c.DisposeAsync(), Times.Once);
    }

    /// <summary>
    /// An unreachable external database throws rather than returning false.
    /// </summary>
    [Test]
    public void UnreachableStorageThrowsAndBacksOff()
    {
        this._database.Setup(d => d.CanConnectAsync(It.IsAny<CancellationToken>())).ReturnsAsync(false);
        var error = Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(error!.Message, Does.Contain("not reachable"));
        Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(this._contextCreations, Is.EqualTo(1));
        this._history.VerifyNoOtherCalls();
    }

    /// <summary>
    /// Connection and history errors escape intact and never mark storage ready.
    /// </summary>
    /// <param name="historyFailure">Whether to fail while reading history.</param>
    [TestCase(false)]
    [TestCase(true)]
    public void ReadErrorsPropagateAndBackOff(bool historyFailure)
    {
        var failure = new InvalidOperationException("Read failure.");
        if (historyFailure)
        {
            this._history.Setup(h => h.GetAppliedMigrationsAsync(It.IsAny<CancellationToken>())).ThrowsAsync(failure);
        }
        else
        {
            this._database.Setup(d => d.CanConnectAsync(It.IsAny<CancellationToken>())).ThrowsAsync(failure);
        }

        var error = Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(error, Is.SameAs(failure));
        var retry = Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(retry!.Message, Does.Contain("probe delay"));
        Assert.That(this._contextCreations, Is.EqualTo(1));
    }

    /// <summary>
    /// An in-flight cancelled read propagates cancellation and records an unsuccessful probe.
    /// </summary>
    [Test]
    public async Task CancelledReadPropagatesAndBacksOffAsync()
    {
        var started = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        this._history.Setup(h => h.GetAppliedMigrationsAsync(It.IsAny<CancellationToken>()))
            .Returns(async (CancellationToken token) =>
            {
                started.TrySetResult();
                await Task.Delay(Timeout.InfiniteTimeSpan, token).ConfigureAwait(false);
                return (IReadOnlyList<HistoryRow>)Array.Empty<HistoryRow>();
            });
        using var cancellation = new CancellationTokenSource();
        var check = this._repository.EnsureStorageAsync(cancellation.Token).AsTask();
        await started.Task.WaitAsync(TestTimeout).ConfigureAwait(false);
        cancellation.Cancel();
        Assert.CatchAsync<OperationCanceledException>(async () => await check.WaitAsync(TestTimeout).ConfigureAwait(false));
        Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(this._contextCreations, Is.EqualTo(1));
    }

    /// <summary>
    /// Concurrent callers share validation; a cancelled lock waiter cannot mark storage ready.
    /// </summary>
    [Test]
    public async Task ConcurrentValidationAndCancelledWaiterAreSafeAsync()
    {
        var release = new TaskCompletionSource<IReadOnlyList<HistoryRow>>(TaskCreationOptions.RunContinuationsAsynchronously);
        this._history.Setup(h => h.GetAppliedMigrationsAsync(It.IsAny<CancellationToken>())).Returns(release.Task);
        var owner = this._repository.EnsureStorageAsync().AsTask();
        using var cancellation = new CancellationTokenSource();
        var cancelledWaiter = this._repository.EnsureStorageAsync(cancellation.Token).AsTask();
        var waiter = this._repository.EnsureStorageAsync().AsTask();
        cancellation.Cancel();
        Assert.CatchAsync<OperationCanceledException>(async () => await cancelledWaiter.WaitAsync(TestTimeout).ConfigureAwait(false));
        Assert.That(owner.IsCompleted, Is.False);
        Assert.That(waiter.IsCompleted, Is.False);
        release.TrySetResult(new[] { new HistoryRow("A", "10.0.2"), new HistoryRow("B", "10.0.2") });
        Assert.That(await owner.WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
        Assert.That(await waiter.WaitAsync(TestTimeout).ConfigureAwait(false), Is.True);
        Assert.That(this._contextCreations, Is.EqualTo(1));
    }

    /// <summary>
    /// A failed check may succeed after the actual production backoff expires.
    /// </summary>
    [Test]
    public async Task FailureCanRetryAfterRealBackoffAsync()
    {
        this._database.SetupSequence(d => d.CanConnectAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(false).ReturnsAsync(true);
        Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.ThrowsAsync<InvalidOperationException>(async () => await this.CheckAsync().ConfigureAwait(false));
        Assert.That(this._contextCreations, Is.EqualTo(1));
        await Task.Delay(TimeSpan.FromSeconds(31)).ConfigureAwait(false);
        Assert.That(await this.CheckAsync().ConfigureAwait(false), Is.True);
        Assert.That(this._contextCreations, Is.EqualTo(2));
    }

    private async Task<bool> CheckAsync()
    {
        return await this._repository.EnsureStorageAsync().AsTask().WaitAsync(TestTimeout).ConfigureAwait(false);
    }

    private void SetHistory(string expected, string applied)
    {
        var migrations = expected.Split(',', StringSplitOptions.RemoveEmptyEntries)
            .ToDictionary(id => id, _ => typeof(AdminPanelContext).GetTypeInfo());
        this._migrations.SetupGet(m => m.Migrations).Returns(migrations);
        IReadOnlyList<HistoryRow> rows = applied.Split(',', StringSplitOptions.RemoveEmptyEntries)
            .Select(id => new HistoryRow(id, "10.0.2")).ToArray();
        this._history.Setup(h => h.GetAppliedMigrationsAsync(It.IsAny<CancellationToken>())).ReturnsAsync(rows);
    }
}

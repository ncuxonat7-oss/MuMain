// <copyright file="AdminUserAvailabilityService.cs" company="MUnique">
// Licensed under the MIT License. See LICENSE file in the project root for full license information.
// </copyright>

namespace MUnique.OpenMU.Web.AdminPanel.Auth;

using System.Threading;
using MUnique.OpenMU.Persistence.AdminAuth;

/// <summary>
/// Keeps track of whether the admin panel has any user at all.
/// </summary>
/// <remarks>
/// On a fresh installation there is neither a database nor a user, and the admin panel is the tool
/// which creates both. Until the first user exists, the panel has to stay reachable - it then runs
/// in an unprotected initial setup mode and says so. Configuring a bootstrap user avoids that state.
/// </remarks>
public class AdminUserAvailabilityService
{
    /// <summary>
    /// The time for which the answer is reused before the storage is asked again.
    /// </summary>
    private static readonly TimeSpan CheckInterval = TimeSpan.FromSeconds(10);

    private readonly IAdminUserRepository _repository;
    private readonly BootstrapAdminUserProvider _bootstrapUserProvider;

    // The semaphore is acquired before the cache lock. Invalidate only takes the cache lock.
    private readonly SemaphoreSlim _semaphore = new(1, 1);
    private readonly object _cacheLock = new();

    private DateTime _nextCheck = DateTime.MinValue;
    private bool _anyUserExists;
    private long _cacheVersion;

    /// <summary>
    /// Initializes a new instance of the <see cref="AdminUserAvailabilityService"/> class.
    /// </summary>
    /// <param name="repository">The repository of the stored users.</param>
    /// <param name="bootstrapUserProvider">The provider of the bootstrap user.</param>
    public AdminUserAvailabilityService(IAdminUserRepository repository, BootstrapAdminUserProvider bootstrapUserProvider)
    {
        this._repository = repository;
        this._bootstrapUserProvider = bootstrapUserProvider;
    }

    /// <summary>
    /// Determines whether at least one user exists which could log in.
    /// </summary>
    /// <param name="cancellationToken">The cancellation token.</param>
    /// <returns><c>true</c>, if a user exists or an invalidated check requires authentication;
    /// otherwise, <c>false</c>.</returns>
    /// <remarks>
    /// Concurrent callers wait for the current check with their own cancellation token. A false
    /// answer is reused only after a completed check, never while the first check is pending.
    /// A check invalidated while in flight requires authentication until a later call rechecks.
    /// </remarks>
    public async ValueTask<bool> AnyUserExistsAsync(CancellationToken cancellationToken = default)
    {
        if (this._bootstrapUserProvider.User is not null)
        {
            return true;
        }

        await this._semaphore.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            long cacheVersion;
            lock (this._cacheLock)
            {
                if (this._anyUserExists || DateTime.UtcNow < this._nextCheck)
                {
                    return this._anyUserExists;
                }

                cacheVersion = this._cacheVersion;
            }

            var anyUserExists = false;
            if (await this._repository.EnsureStorageAsync(cancellationToken).ConfigureAwait(false))
            {
                anyUserExists = await this._repository.GetCountAsync(cancellationToken).ConfigureAwait(false) > 0;
            }

            cancellationToken.ThrowIfCancellationRequested();
            lock (this._cacheLock)
            {
                if (cacheVersion != this._cacheVersion)
                {
                    // Invalidate superseded this check. Do not open initial setup or cache its result.
                    return true;
                }

                // A false storage result preserves the default mode's initial setup behavior.
                // External storage errors propagate before any result is cached.
                this._anyUserExists = anyUserExists;
                this._nextCheck = DateTime.UtcNow.Add(CheckInterval);
                return this._anyUserExists;
            }
        }
        finally
        {
            this._semaphore.Release();
        }
    }

    /// <summary>
    /// Invalidates the cached result, e.g. after a user has been created or deleted.
    /// </summary>
    public void Invalidate()
    {
        lock (this._cacheLock)
        {
            this._cacheVersion++;
            this._anyUserExists = false;
            this._nextCheck = DateTime.MinValue;
        }
    }
}

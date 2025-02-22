using MovieLibrary.Core.Models;
using MovieLibrary.Core.Models.Nulls;

namespace MovieLibrary.Core.Contracts.Repositories;

public interface IUserRepository : IRepository<User>
{
    /// <summary>
    /// Gets a single user by its username.
    /// </summary>
    /// <param name="username">The user's username.</param>
    /// <returns>The user if the given username exists. Otherwise,
    /// an instance of its null object (<see cref="NullUser"/>).</returns>
    Task<User> GetByUsernameAsync(string username);
}

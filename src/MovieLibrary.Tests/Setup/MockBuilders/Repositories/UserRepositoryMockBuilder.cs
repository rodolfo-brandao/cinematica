using System.Linq.Expressions;
using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Models;
using MovieLibrary.Tests.Setup.MockBuilders.Abstract;

namespace MovieLibrary.Tests.Setup.MockBuilders.Repositories;

/// <summary>
/// A builder to expose mock functionalities of <see cref="IUserRepository"/>.
/// </summary>
internal sealed class UserRepositoryMockBuilder : BaseMockBuilder<UserRepositoryMockBuilder, IUserRepository>
{
    /// <summary>
    /// Mocks the 'ExistsAsync()' method.
    /// </summary>
    /// <param name="exists">
    /// Defines whether a user exists or not.
    /// Use this parameter to configure the behavior of the mocked
    /// method according to the test scenario.
    /// </param>
    /// <returns>The <see cref="UserRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public UserRepositoryMockBuilder SetupExistsAsync(bool exists = false)
    {
        Mock.Setup(userRepository => userRepository.ExistsAsync(It.IsAny<Expression<Func<User, bool>>>())).ReturnsAsync(exists);
        return this;
    }

    /// <summary>
    /// Mocks the 'InsertAsync()' method.
    /// </summary>
    /// <param name="user">
    /// The user model to be used as inserted one.
    /// Use this parameter to configure the behavior of the mocked
    /// method according to the test scenario.
    /// </param>
    /// <returns>The <see cref="UserRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public UserRepositoryMockBuilder SetupInsertAsync(User user)
    {
        Mock.Setup(repository => repository.InsertAsync(It.IsAny<User>())).ReturnsAsync(user);
        return this;
    }
}

using System.Linq.Expressions;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;
using Cinematica.Core.Models.Nulls;
using Cinematica.Tests.Setup.MockBuilders.Abstract;

namespace Cinematica.Tests.Setup.MockBuilders.Repositories;

/// <summary>
/// A builder to expose mock functionalities of <see cref="IUserRepository"/>.
/// </summary>
internal sealed class UserRepositoryMockBuilder : BaseMockBuilder<UserRepositoryMockBuilder, IUserRepository>
{
    /// <summary>
    /// Mocks the 'ExistsAsync()' method.
    /// </summary>
    /// <param name="exists">Defines whether a user exists or not.</param>
    /// <returns>The <see cref="UserRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public UserRepositoryMockBuilder SetupExistsAsync(bool exists = false)
    {
        Mock.Setup(repository => repository.ExistsAsync(It.IsAny<Expression<Func<User, bool>>>())).ReturnsAsync(exists);
        return this;
    }

    /// <summary>
    /// Mocks the 'GetByUsernameAsync()' method.
    /// </summary>
    /// <param name="user">
    /// The model to be used as the existing user.
    /// If no model is given, an instance of <see cref="NullUser"/> will be returned.
    /// </param>
    /// <returns>The <see cref="UserRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public UserRepositoryMockBuilder SetupGetByUsernameAsync(User? user = null)
    {
        Mock.Setup(repository => repository.GetByUsernameAsync(It.IsAny<string>())).ReturnsAsync(user ?? new NullUser());
        return this;
    }

    /// <summary>
    /// Mocks the 'InsertAsync()' method.
    /// </summary>
    /// <param name="user">The user model to be used as the inserted one.</param>
    /// <returns>The <see cref="UserRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public UserRepositoryMockBuilder SetupInsertAsync(User user)
    {
        Mock.Setup(repository => repository.InsertAsync(It.IsAny<User>())).ReturnsAsync(user);
        return this;
    }
}
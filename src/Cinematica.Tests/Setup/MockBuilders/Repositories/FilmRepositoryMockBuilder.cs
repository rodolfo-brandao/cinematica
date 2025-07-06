using System.Linq.Expressions;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Abstract;

namespace Cinematica.Tests.Setup.MockBuilders.Repositories;

/// <summary>
/// A builder to expose mock functionalities of <see cref="IFilmRepository"/>.
/// </summary>
internal sealed class FilmRepositoryMockBuilder : BaseMockBuilder<FilmRepositoryMockBuilder, IFilmRepository>
{
    /// <summary>
    /// Mocks the 'Query()' method.
    /// </summary>
    /// <param name="films">The predefined query of films to be returned by the mocked method.</param>
    /// <param name="count">
    /// The count of fake models to be randomly generated and returned by the mocked method.
    /// This parameter is ignored if the first one is passed.
    /// </param>
    /// <returns>The <see cref="FilmRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public FilmRepositoryMockBuilder SetupQuery(IQueryable<Film> films = null, int count = 10)
    {
        Mock.Setup(repository => repository.Query(
                It.IsAny<Expression<Func<Film, bool>>>(),
                It.IsAny<string>(),
                It.IsAny<bool>()))
            .Returns(films ?? FilmFake.GetMany(count).AsQueryable());
        return this;
    }
}
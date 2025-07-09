using Cinematica.Application.Queries.Films.ListFilms;
using Cinematica.Application.Responses.Films;
using Cinematica.Application.Utils;
using Cinematica.Core.Models;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Repositories;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Tests.Application.Queries.Films.ListFilms;

[Trait(name: "Handler(query)", value: "ListFilms")]
public class ListFilmsHandlerTest
{
    [Fact(DisplayName = "[async] Handle() - Success case: query has valid parameter values")]
    public async Task Handle_QueryHasValidParameterValues_HandlerShouldReturnListOfFilms()
    {
        // Arrange:
        var director = DirectorFake.Valid();
        var country = CountryFake.Valid();
        var genre = GenreFake.Valid();
        var filmGenre = FilmGenreFake.Valid(genre: genre);
        var film = FilmFake.Valid(director, country, filmGenre);
        var query = new ListFilmsQuery
        {
            Name = film.Name,
            Year = film.ReleaseYear,
            CountryCode = country.IsoAlpha3Code
        };

        var filmsQuery = new List<Film> { film }.AsQueryable();
        var filmRepository = FilmRepositoryMockBuilder
            .Create()
            .SetupQuery(filmsQuery)
            .Build();

        var handler = new ListFilmsHandler(filmRepository);

        // Act:
        var sut = await handler.Handle(query, cancellationToken: CancellationToken.None);

        // Assert:
        Assert.NotNull(sut);
        Assert.IsType<ApiResult<IEnumerable<DefaultFilmResponse>>>(sut);
        Assert.Equal(expected: StatusCodes.Status200OK, actual: sut.StatusCode);
        Assert.NotEmpty(sut.Response);
    }
}

using Cinematica.Application.Responses.Films;
using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Queries;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;

namespace Cinematica.Application.Queries.Films.ListFilms;

public class ListFilmsHandler(IFilmRepository filmRepository)
    : ISort<Film>, IFilter<ListFilmsQuery, Film>,
    IRequestHandler<ListFilmsQuery, ApiResult<IEnumerable<DefaultFilmResponse>>>
{
    public async Task<ApiResult<IEnumerable<DefaultFilmResponse>>> Handle(ListFilmsQuery request,
        CancellationToken cancellationToken)
    {
        const string included = $"{nameof(Country)}" +
                                $",{nameof(Director)}" +
                                $",{nameof(FilmGenre)}s" +
                                $",{nameof(FilmGenre)}s.{nameof(Genre)}";

        var films = filmRepository.Query(
            expression: _ => true,
            isReadOnly: true,
            includes: included);

        var filteredFilms = Filter(request, films);
        var apiResult = new ApiResult<IEnumerable<DefaultFilmResponse>>
        {
            Response = [.. filteredFilms.Select(film => new DefaultFilmResponse
            {
                Id = film.Id,
                Name = film.Name,
                OriginalName = film.OriginalName,
                Year = film.ReleaseYear,
                Runtime = $"{film.RuntimeInMinutes}min",
                Synopsis = film.Synopsis,
                Director = film.Director.Name,
                Country = film.Country.IsoAlpha3Code,
                Genres = FormatFilmGenres(film.FilmGenres)
            })]
        };

        return await Task.FromResult(apiResult);
    }

    #region Query Tools

    public IQueryable<Film> Filter(ListFilmsQuery query, IQueryable<Film> entities)
    {
        if (!string.IsNullOrWhiteSpace(query.Name))
        {
            entities = entities.Where(film => film.Name.ToLower().Contains(query.Name.ToLower()));
        }

        if (!string.IsNullOrWhiteSpace(query.Year))
        {
            entities = entities.Where(film => film.ReleaseYear.Equals(query.Year));
        }

        if (!string.IsNullOrWhiteSpace(query.CountryCode))
        {
            entities = entities.Where(film => film.Country.IsoAlpha3Code.ToLower().Equals(query.CountryCode.ToLower()));
        }

        entities = Sort(query.SortBy, query.Direction, entities);
        return entities.Skip((query.Page - 1) * query.PageSize).Take(query.PageSize);
    }

    public IQueryable<Film> Sort(string field, string direction, IQueryable<Film> entities)
    {
        if (direction.Equals("desc"))
        {
            entities = field switch
            {
                "year" => entities.OrderByDescending(film => film.ReleaseYear),
                "country" => entities.OrderByDescending(film => film.Country.IsoAlpha3Code),
                "runtime" => entities.OrderByDescending(film => film.RuntimeInMinutes),
                _ => entities.OrderByDescending(film => film.Name)
            };
        }
        else
        {
            entities = field switch
            {
                "year" => entities.OrderBy(film => film.ReleaseYear),
                "country" => entities.OrderBy(film => film.Country.IsoAlpha3Code),
                "runtime" => entities.OrderBy(film => film.RuntimeInMinutes),
                _ => entities.OrderBy(film => film.Name)
            };
        }

        return entities;
    }

    #endregion

    #region Private Methods

    private static string FormatFilmGenres(ICollection<FilmGenre> filmGenres)
    {
        return string.Join(separator: ", ", values: filmGenres.Select(filmGenre => filmGenre.Genre.Name));
    }

    #endregion
}

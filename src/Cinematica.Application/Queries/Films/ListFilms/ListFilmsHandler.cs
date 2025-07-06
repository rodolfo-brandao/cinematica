using Cinematica.Application.Responses.Films;
using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;

namespace Cinematica.Application.Queries.Films.ListFilms;

public class ListFilmsHandler(IFilmRepository filmRepository)
    : IRequestHandler<ListFilmsQuery, ApiResult<IEnumerable<DefaultFilmResponse>>>
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

        var filteredFilms = ApplyFilters(request, films);
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

    #region Private Methods

    private static IQueryable<Film> ApplyFilters(ListFilmsQuery query, IQueryable<Film> films)
    {
        if (!string.IsNullOrWhiteSpace(query.Name))
        {
            films = films.Where(film => film.Name.ToLower().Contains(query.Name.ToLower()));
        }

        if (!string.IsNullOrWhiteSpace(query.Year))
        {
            films = films.Where(film => film.ReleaseYear.Equals(query.Year));
        }

        if (!string.IsNullOrWhiteSpace(query.CountryCode))
        {
            films = films.Where(film => film.Country.IsoAlpha3Code.ToLower().Equals(query.CountryCode.ToLower()));
        }

        films = ApplySorting(query.SortBy, query.Direction, films);
        return films.Skip((query.Page - 1) * query.PageSize).Take(query.PageSize);
    }

    private static IQueryable<Film> ApplySorting(string field, string direction, IQueryable<Film> films)
    {
        if (direction.Equals("desc"))
        {
            films = field switch
            {
                "year" => films.OrderByDescending(film => film.ReleaseYear),
                "country" => films.OrderByDescending(film => film.Country.IsoAlpha3Code),
                "runtime" => films.OrderByDescending(film => film.RuntimeInMinutes),
                _ => films.OrderByDescending(film => film.Name)
            };
        }
        else
        {
            films = field switch
            {
                "year" => films.OrderBy(film => film.ReleaseYear),
                "country" => films.OrderBy(film => film.Country.IsoAlpha3Code),
                "runtime" => films.OrderBy(film => film.RuntimeInMinutes),
                _ => films.OrderBy(film => film.Name)
            };
        }

        return films;
    }

    private static string FormatFilmGenres(ICollection<FilmGenre> filmGenres)
    {
        return string.Join(separator: ", ", values: filmGenres.Select(filmGenre => filmGenre.Genre.Name));
    }

    #endregion
}

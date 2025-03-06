using Cinematica.Application.Responses.Films;
using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace Cinematica.Application.Queries.Films.ListFilms;

public class ListFilmsHandler(IFilmRepository filmRepository)
    : IRequestHandler<ListFilmsQuery, ApiResult<IEnumerable<DefaultFilmResponse>>>
{
    public async Task<ApiResult<IEnumerable<DefaultFilmResponse>>> Handle(ListFilmsQuery request,
        CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<IEnumerable<DefaultFilmResponse>>();
        const string included =
            $"{nameof(Country)},{nameof(Director)},{nameof(FilmGenre)}s,{nameof(FilmGenre)}s.{nameof(Genre)}";
        var movies = filmRepository.Query(_ => true, isReadOnly: true, includes: included);
        var filteredFilms = await ApplyFilters(request, movies);
        apiResult.Response = filteredFilms.Select(film => new DefaultFilmResponse
        {
            Id = film.Id,
            Name = film.Name,
            OriginalName = film.OriginalName,
            Year = film.ReleaseYear,
            Runtime = $"{film.RuntimeInMinutes}min",
            Synopsis = film.Synopsis,
            Director = film.Director.Name,
            Country = film.Country.IsoAlpha3Code,
            Genres = string.Join(separator: ", ", values: film.FilmGenres.Select(filmGenre => filmGenre.Genre.Name))
        });
        return apiResult;
    }

    #region Private Methods

    private static async Task<IList<Film>> ApplyFilters(ListFilmsQuery query, IQueryable<Film> films)
    {
        if (!string.IsNullOrWhiteSpace(query.Name))
        {
            films = films.Where(film => EF.Functions.Like(film.Name, $"%{query.Name}%"));
        }

        if (!string.IsNullOrWhiteSpace(query.Year))
        {
            films = films.Where(film => film.ReleaseYear.Equals(query.Year));
        }

        if (!string.IsNullOrWhiteSpace(query.CountryCode))
        {
            films = films.Where(film => EF.Functions.Like(film.Country.IsoAlpha3Code, $"%{query.CountryCode}%"));
        }

        films = ApplySorting(query.SortBy, query.Direction, films);
        films = films.Skip((query.Page - 1) * query.PageSize).Take(query.PageSize);
        return await films.ToListAsync();
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

    #endregion
}
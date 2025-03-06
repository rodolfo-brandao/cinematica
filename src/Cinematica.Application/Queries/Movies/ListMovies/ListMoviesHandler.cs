using Microsoft.EntityFrameworkCore;
using Cinematica.Application.Responses.Movies;
using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;

namespace Cinematica.Application.Queries.Movies.ListMovies;

public class ListMoviesHandler(IMovieRepository movieRepository)
    : IRequestHandler<ListMoviesQuery, ApiResult<IEnumerable<DefaultMovieResponse>>>
{
    public async Task<ApiResult<IEnumerable<DefaultMovieResponse>>> Handle(ListMoviesQuery request,
        CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<IEnumerable<DefaultMovieResponse>>();
        const string included =
            $"{nameof(Country)},{nameof(Director)},{nameof(MovieGenre)}s,{nameof(MovieGenre)}s.{nameof(Genre)}";
        var movies = movieRepository.Query(_ => true, isReadOnly: true, includes: included);
        var filteredMovies = await ApplyFilters(request, movies);
        apiResult.Response = filteredMovies.Select(movie => new DefaultMovieResponse
        {
            Id = movie.Id,
            Name = movie.Name,
            OriginalName = movie.OriginalName,
            Year = movie.ReleaseYear,
            Runtime = $"{movie.RuntimeInMinutes}min",
            Synopsis = movie.Synopsis,
            Director = movie.Director.Name,
            Country = movie.Country.IsoAlpha3Code,
            Genres = string.Join(", ", movie.MovieGenres.Select(movieGenre => movieGenre.Genre.Name))
        });
        return apiResult;
    }

    #region Private Methods

    private static async Task<IList<Movie>> ApplyFilters(ListMoviesQuery query, IQueryable<Movie> movies)
    {
        if (!string.IsNullOrWhiteSpace(query.Name))
        {
            movies = movies.Where(movie => EF.Functions.Like(movie.Name, $"%{query.Name}%"));
        }

        if (!string.IsNullOrWhiteSpace(query.Year))
        {
            movies = movies.Where(movie => movie.ReleaseYear.Equals(query.Year));
        }

        if (!string.IsNullOrWhiteSpace(query.CountryCode))
        {
            movies = movies.Where(movie => EF.Functions.Like(movie.Country.IsoAlpha3Code, $"%{query.CountryCode}%"));
        }

        movies = ApplySorting(query.SortBy, query.Direction, movies);
        movies = movies.Skip((query.Page - 1) * query.PageSize).Take(query.PageSize);
        return await movies.ToListAsync();
    }

    private static IQueryable<Movie> ApplySorting(string field, string direction, IQueryable<Movie> movies)
    {
        if (direction.Equals("desc"))
        {
            movies = field switch
            {
                "year" => movies.OrderByDescending(movie => movie.ReleaseYear),
                "country" => movies.OrderByDescending(movie => movie.Country.IsoAlpha3Code),
                "runtime" => movies.OrderByDescending(movie => movie.RuntimeInMinutes),
                _ => movies.OrderByDescending(movie => movie.Name)
            };
        }
        else
        {
            movies = field switch
            {
                "year" => movies.OrderBy(movie => movie.ReleaseYear),
                "country" => movies.OrderBy(movie => movie.Country.IsoAlpha3Code),
                "runtime" => movies.OrderBy(movie => movie.RuntimeInMinutes),
                _ => movies.OrderBy(movie => movie.Name)
            };
        }

        return movies;
    }

    #endregion
}
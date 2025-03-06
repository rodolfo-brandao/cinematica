using Microsoft.AspNetCore.Mvc;
using Cinematica.Application.Responses.Movies;
using Cinematica.Application.Utils;
using Cinematica.Application.Utils.QueryTools.Abstract;

namespace Cinematica.Application.Queries.Movies.ListMovies;

public class ListMoviesQuery : BaseQueryParams, IRequest<ApiResult<IEnumerable<DefaultMovieResponse>>>
{
    /// <summary>
    /// The name, or a substring, of a movie (case-insensitive).
    /// </summary>
    [FromQuery(Name = "name")]
    public string Name { get; set; }

    /// <summary>
    /// The release year of a movie.
    /// </summary>
    [FromQuery(Name = "year")]
    public string Year { get; set; }

    /// <summary>
    /// The ISO 3166-1 country code of which a movie was released (e.g. USA, JPN [case-insensitive]).
    /// </summary>
    [FromQuery(Name = "country_code")]
    public string CountryCode { get; set; }
}
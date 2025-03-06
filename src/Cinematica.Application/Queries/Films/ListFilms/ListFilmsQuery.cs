using Cinematica.Application.Responses.Films;
using Cinematica.Application.Utils;
using Cinematica.Application.Utils.QueryTools.Abstract;
using Microsoft.AspNetCore.Mvc;

namespace Cinematica.Application.Queries.Films.ListFilms;

public class ListFilmsQuery : BaseQueryParams, IRequest<ApiResult<IEnumerable<DefaultFilmResponse>>>
{
    /// <summary>
    /// The name, or a substring, of a film (case-insensitive).
    /// </summary>
    [FromQuery(Name = "name")]
    public string Name { get; set; }

    /// <summary>
    /// The release year of a film.
    /// </summary>
    [FromQuery(Name = "year")]
    public string Year { get; set; }

    /// <summary>
    /// The ISO 3166-1 country code of which a film was released (e.g. USA, JPN [case-insensitive]).
    /// </summary>
    [FromQuery(Name = "country_code")]
    public string CountryCode { get; set; }
}
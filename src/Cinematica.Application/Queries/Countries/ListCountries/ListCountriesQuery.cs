using Cinematica.Application.Responses.Countries;
using Cinematica.Application.Utils;
using Cinematica.Application.Utils.QueryTools.Abstract;
using Cinematica.Core.Contracts.Queries;
using Microsoft.AspNetCore.Mvc;

namespace Cinematica.Application.Queries.Countries.ListCountries;

public class ListCountriesQuery : BaseQueryParams,
    IQuery, IRequest<ApiResult<IEnumerable<DefaultCountryResponse>>>
{
    /// <summary>
    /// The full name or a substring (case-insensitive).
    /// </summary>
    [FromQuery(Name = "name")]
    public string Name { get; set; }

    /// <summary>
    /// The ISO 3166-1 code (e.g. USA, JPN [case-insensitive]).
    /// </summary>
    [FromQuery(Name = "code")]
    public string IsoCode { get; set; }
}

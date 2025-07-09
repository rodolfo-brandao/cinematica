using Cinematica.Application.Responses.Countries;
using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Queries;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;

namespace Cinematica.Application.Queries.Countries.ListCountries;

public class ListCountriesHandler(ICountryRepository countryRepository)
    : ISort<Country>, IFilter<ListCountriesQuery, Country>,
    IRequestHandler<ListCountriesQuery, ApiResult<IEnumerable<DefaultCountryResponse>>>
{
    public async Task<ApiResult<IEnumerable<DefaultCountryResponse>>> Handle(ListCountriesQuery request,
        CancellationToken cancellationToken)
    {
        var countries = countryRepository.Query(expression: country => !country.IsDisabled);
        var filteredCountries = Filter(request, countries);
        var apiResult = new ApiResult<IEnumerable<DefaultCountryResponse>>
        {
            Response = [.. filteredCountries.Select(country => new DefaultCountryResponse {
                Id = country.Id,
                Name = country.Name,
                Code = country.IsoAlpha3Code
            })]
        };

        return await Task.FromResult(apiResult);
    }

    #region Query Tools

    public IQueryable<Country> Filter(ListCountriesQuery query, IQueryable<Country> entities)
    {
        if (!string.IsNullOrWhiteSpace(query.Name))
        {
            entities = entities.Where(country => country.Name.ToLower().Contains(query.Name.ToLower()));
        }

        if (!string.IsNullOrWhiteSpace(query.IsoCode))
        {
            entities = entities.Where(country => country.IsoAlpha3Code.Equals(query.IsoCode));
        }

        entities = Sort(query.SortBy, query.Direction, entities);
        return entities.Skip((query.Page - 1) * query.PageSize).Take(query.PageSize);
    }

    public IQueryable<Country> Sort(string field, string direction, IQueryable<Country> entities)
    {
        if (direction.Equals("desc"))
        {
            entities = field switch
            {
                "code" => entities.OrderByDescending(country => country.IsoAlpha3Code),
                _ => entities.OrderByDescending(film => film.Name)
            };
        }
        else
        {
            entities = field switch
            {
                "code" => entities.OrderBy(country => country.IsoAlpha3Code),
                _ => entities.OrderBy(film => film.Name)
            };
        }

        return entities;
    }

    #endregion
}

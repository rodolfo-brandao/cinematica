using Cinematica.Application.Queries.Countries.ListCountries;
using Cinematica.Application.Responses.Countries;
using Cinematica.Application.Utils;
using Cinematica.Core.Models;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Repositories;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Tests.Application.Queries.Countries.ListCountries;

[Trait(name: "Handler(query)", value: "ListCountries")]
public class ListCountriesHandlerTest
{
    [Fact(DisplayName = "[async] Handle() - Success case: query has valid parameter values")]
    public async Task Handle_QueryHasValidParameterValues_HandlerShouldReturnListOfCountries()
    {
        // Arrange:
        var country = CountryFake.Valid();
        var query = new ListCountriesQuery
        {
            Name = country.Name,
            IsoCode = country.IsoAlpha3Code
        };

        var countriesQuery = new List<Country> { country }.AsQueryable();
        var cancellationToken = CancellationToken.None;
        var countryRepository = CountryRepositoryMockBuilder
            .Create()
            .SetupQuery(countriesQuery)
            .Build();

        var handler = new ListCountriesHandler(countryRepository);

        // Act:
        var sut = await handler.Handle(query, cancellationToken: CancellationToken.None);

        // Assert:
        Assert.NotNull(sut);
        Assert.IsType<ApiResult<IEnumerable<DefaultCountryResponse>>>(sut);
        Assert.Equal(expected: StatusCodes.Status200OK, actual: sut.StatusCode);
        Assert.NotEmpty(sut.Response);
    }
}

using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Models;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Abstract;
using System.Linq.Expressions;

namespace Cinematica.Tests.Setup.MockBuilders.Repositories;

/// <summary>
/// A builder to expose mock methods from <see cref="ICountryRepository"/>.
/// </summary>
internal class CountryRepositoryMockBuilder : BaseMockBuilder<CountryRepositoryMockBuilder, ICountryRepository>
{
    /// <summary>
    /// Mocks the 'GetByKeyAsync()' method.
    /// </summary>
    /// <param name="country">
    /// The model to be used as the existing country.
    /// If no model is given, a fake instance of <see cref="Country"/> will be returned.
    /// </param>
    /// <returns>The <see cref="CountryRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public CountryRepositoryMockBuilder SetupGetByKeyAsync(Country country = default)
    {
        Mock.Setup(repository => repository.GetByKeyAsync(It.IsAny<object[]>())).ReturnsAsync(country ?? CountryFake.Valid());
        return this;
    }

    /// <summary>
    /// Mocks the 'Query()' method.
    /// </summary>
    /// <param name="countries">The predefined query of countries to be returned by the mocked method.</param>
    /// <param name="count">
    /// The count of fake models to be randomly generated and returned by the mocked method.
    /// This parameter is ignored if the first one is passed.
    /// </param>
    /// <returns>The <see cref="CountryRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public CountryRepositoryMockBuilder SetupQuery(IQueryable<Country> countries = default, int count = 10)
    {
        Mock.Setup(repository => repository.Query(
            It.IsAny<Expression<Func<Country, bool>>>(),
            It.IsAny<string>(),
            It.IsAny<bool>()))
        .Returns(countries ?? CountryFake.GetMany(count).AsQueryable());

        return this;
    }

    /// <summary>
    /// Mocks the 'Remove()' method.
    /// </summary>
    /// <param name="country">
    /// The model to be used as the existing country.
    /// If no model is given, a fake instance of <see cref="Country"/> will be returned.
    /// </param>
    /// <returns>The <see cref="CountryRepositoryMockBuilder"/> so that additional calls can be chained.</returns>
    public CountryRepositoryMockBuilder SetupRemove(Country country = default)
    {
        Mock.Setup(repository => repository.Remove(It.IsAny<Country>())).Returns(country ?? CountryFake.Valid());
        return this;
    }
}

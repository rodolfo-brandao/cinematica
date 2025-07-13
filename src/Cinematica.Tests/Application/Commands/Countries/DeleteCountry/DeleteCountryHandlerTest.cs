using Cinematica.Application.Commands.Countries.DeleteCountry;
using Cinematica.Application.Utils;
using Cinematica.Tests.Setup.MockBuilders.Repositories;
using Cinematica.Tests.Setup.MockBuilders.Units;
using MediatR;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Tests.Application.Commands.Countries.DeleteCountry;

[Trait(name: "Handler(command)", value: "DeleteCountry")]
public class DeleteCountryHandlerTest
{
    [Fact(DisplayName = "[async] Handle() - Success case: country exists and is removed")]
    public async Task Handle_CountryExists_HandlerShouldDeleteCountrySuccessfully()
    {
        // Arrange:
        var anyCountryId = Guid.NewGuid();
        var command = new DeleteCountryCommand(anyCountryId);
        var cancellationToken = CancellationToken.None;

        var countryRepository = CountryRepositoryMockBuilder
            .Create()
            .SetupGetByKeyAsync()
            .SetupRemove()
            .Build();

        var unitOfWork = UnitOfWorkMockBuilder
            .Create()
            .SetupSaveChangesAsync()
            .Build();

        var handler = new DeleteCountryHandler(countryRepository, unitOfWork);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<Unit>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(expected: StatusCodes.Status204NoContent, actual: sut.StatusCode);
    }

    #region Failure Cases

    [Fact(DisplayName = "[async] Handle() - Failure case: country does not exist and therefore is not found.")]
    public async Task Handle_CountryDoesNotExist_HandlerShouldIndicateCountryNotFound()
    {
        // Arrange:
        var anyCountryId = Guid.NewGuid();
        var command = new DeleteCountryCommand(anyCountryId);
        var cancellationToken = CancellationToken.None;

        var countryRepository = CountryRepositoryMockBuilder.Create()
            .SetupRemove()
            .Build();

        var unitOfWork = UnitOfWorkMockBuilder
            .Create()
            .SetupSaveChangesAsync()
            .Build();

        var handler = new DeleteCountryHandler(countryRepository, unitOfWork);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<Unit>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(expected: StatusCodes.Status404NotFound, actual: sut.StatusCode);
        Assert.NotNull(sut.ErrorMessage);
    }

    #endregion
}

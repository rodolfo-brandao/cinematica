using Cinematica.Application.Commands.Users.DeleteUser;
using Cinematica.Application.Utils;
using Cinematica.Tests.Setup.MockBuilders.Repositories;
using Cinematica.Tests.Setup.MockBuilders.Units;
using MediatR;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Tests.Application.Commands.Users.DeleteUser;

[Trait(name: "Handler(command)", value: "DeleteUser")]
public class DeleteUserHandlerTest
{
    [Fact(DisplayName = "[async] Handle() - Success case: user exists and is removed")]
    public async Task Handle_UserExists_HandlerShouldDeleteUserSuccessfully()
    {
        // Arrange:
        var anyUserId = Guid.NewGuid();
        var command = new DeleteUserCommand(anyUserId);
        var cancellationToken = CancellationToken.None;

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupGetByKeyAsync()
            .SetupRemove()
            .Build();

        var unitOfWork = UnitOfWorkMockBuilder
            .Create()
            .SetupSaveChangesAsync()
            .Build();

        var handler = new DeleteUserHandler(userRepository, unitOfWork);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<Unit>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(expected: StatusCodes.Status204NoContent, actual: sut.StatusCode);
    }

    #region Failure Cases

    [Fact(DisplayName = "[async] Handle() - Failure case: user does not exist and therefore is not found.")]
    public async Task Handle_UserDoesNotExist_HandlerShouldIndicateUserNotFound()
    {
        // Arrange:
        var anyUserId = Guid.NewGuid();
        var command = new DeleteUserCommand(anyUserId);
        var cancellationToken = CancellationToken.None;

        var userRepository = UserRepositoryMockBuilder.Create()
            .SetupRemove()
            .Build();

        var unitOfWork = UnitOfWorkMockBuilder
            .Create()
            .SetupSaveChangesAsync()
            .Build();

        var handler = new DeleteUserHandler(userRepository, unitOfWork);

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

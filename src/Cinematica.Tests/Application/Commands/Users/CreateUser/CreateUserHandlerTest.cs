using Microsoft.AspNetCore.Http;
using Cinematica.Application.Commands.Users.CreateUser;
using Cinematica.Application.Responses.Users;
using Cinematica.Application.Utils;
using Cinematica.Tests.Setup.Fakers.Commands.Users.CreateUser;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Factories;
using Cinematica.Tests.Setup.MockBuilders.Repositories;
using Cinematica.Tests.Setup.MockBuilders.Services;
using Cinematica.Tests.Setup.MockBuilders.Units;

namespace Cinematica.Tests.Application.Commands.Users.CreateUser;

[Trait(name: "Handler", value: "CreateUser")]
public class CreateUserHandlerTest
{
    [Fact(DisplayName = "Handle() - Success case: payload is valid")]
    public async Task Handle_PassValidPayload_HandlerShouldCreateUser()
    {
        // Arrange:
        var command = CreateUserCommandFake.Valid();
        var cancellationTokenSource = new CancellationTokenSource();
        var cancellationToken = cancellationTokenSource.Token;
        var user = UserFake.Valid();

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupInsertAsync(user)
            .Build();

        var unitOfWork = UnitOfWorkMockBuilder
            .Create()
            .SetupSaveChangesAsync()
            .Build();

        var securityService = SecurityServiceMockBuilder
            .Create()
            .SetupCreatePasswordHash(user.Password, user.PasswordSalt)
            .Build();
        
        var modelFactory = ModelFactoryMockBuilder
            .Create()
            .SetupCreateUser()
            .Build();

        var handler = new CreateUserHandler(userRepository, securityService, unitOfWork, modelFactory);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<CreatedUserResponse>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(StatusCodes.Status200OK, sut.StatusCode);
        Assert.NotNull(sut.Response);
    }
}
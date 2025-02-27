using MovieLibrary.Application.Commands.Users.CreateUser;
using MovieLibrary.Application.Responses.Users;
using MovieLibrary.Application.Utils;
using MovieLibrary.Tests.Setup.Fakers.Commands.Users.CreateUser;
using MovieLibrary.Tests.Setup.Fakers.Models;
using MovieLibrary.Tests.Setup.MockBuilders.Factories;
using MovieLibrary.Tests.Setup.MockBuilders.Repositories;
using MovieLibrary.Tests.Setup.MockBuilders.Services;
using MovieLibrary.Tests.Setup.MockBuilders.Units;

namespace MovieLibrary.Tests.Application.Commands.Users.CreateUser;

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
    }
}
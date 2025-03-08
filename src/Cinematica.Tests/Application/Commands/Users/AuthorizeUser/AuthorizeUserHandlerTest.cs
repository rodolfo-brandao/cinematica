using Cinematica.Application.Commands.Users.AuthorizeUser;
using Cinematica.Application.Responses.Users;
using Cinematica.Application.Utils;
using Cinematica.Tests.Setup.Fakers.Commands.Users.AuthorizeUser;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Repositories;
using Cinematica.Tests.Setup.MockBuilders.Services;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Tests.Application.Commands.Users.AuthorizeUser;

[Trait(name: "Handler", value: "AuthorizeUser")]
public class AuthorizeUserHandlerTest
{
    [Fact(DisplayName = "Handle() - Success case: payload is valid")]
    public async Task Handle_PassValidPayload_HandlerShouldCreateJsonWebToken()
    {
        // Arrange:
        var command = AuthorizeUserCommandFake.Valid();
        var cancellationToken = new CancellationTokenSource().Token;
        var user = UserFake.Valid(command.Username);

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupGetByUsernameAsync(user)
            .Build();

        var securityService = SecurityServiceMockBuilder
            .Create()
            .SetupValidatePassword()
            .Build();

        var handler = new AuthorizeUserHandler(userRepository, securityService);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<AuthorizedUserResponse>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(expected: StatusCodes.Status200OK, actual: sut.StatusCode);
        Assert.NotNull(sut.Response);
    }

    #region Failure cases

    [Fact(DisplayName = "Handle() - Failure case: invalid username")]
    public async Task Handle_PassPayloadWithInvalidUsername_HandlerShouldNotIssueJsonWebToken()
    {
        // Arrange:
        var command = new AuthorizeUserCommand
        {
            Username = "anyUsername",
            Password = string.Empty
        };
        var cancellationToken = new CancellationTokenSource().Token;

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupGetByUsernameAsync()
            .Build();

        var securityService = SecurityServiceMockBuilder
            .Create()
            .SetupValidatePassword()
            .Build();

        var handler = new AuthorizeUserHandler(userRepository, securityService);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<AuthorizedUserResponse>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(expected: StatusCodes.Status400BadRequest, actual: sut.StatusCode);
        Assert.Null(sut.Response);
        Assert.NotNull(sut.ErrorMessage);
        Assert.NotEqual(expected: string.Empty, actual: sut.ErrorMessage);
    }

    [Fact(DisplayName = "Handle() - Failure case: invalid password")]
    public async Task Handle_PassPayloadWithInvalidPassword_HandlerShouldNotIssueJsonWebToken()
    {
        // Arrange:
        var command = new AuthorizeUserCommand
        {
            Username = string.Empty,
            Password = "anyPassword"
        };
        var user = UserFake.Valid(command.Username);
        var cancellationToken = new CancellationTokenSource().Token;

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupGetByUsernameAsync(user)
            .Build();

        var securityService = SecurityServiceMockBuilder
            .Create()
            .SetupValidatePassword(isValid: false)
            .Build();

        var handler = new AuthorizeUserHandler(userRepository, securityService);

        // Act:
        var sut = await handler.Handle(command, cancellationToken);

        // Assert:
        Assert.IsType<ApiResult<AuthorizedUserResponse>>(sut);
        Assert.NotNull(sut);
        Assert.Equal(expected: StatusCodes.Status400BadRequest, actual: sut.StatusCode);
        Assert.Null(sut.Response);
        Assert.NotNull(sut.ErrorMessage);
        Assert.NotEqual(expected: string.Empty, actual: sut.ErrorMessage);
    }

    #endregion
}
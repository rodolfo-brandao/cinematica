using Cinematica.Application.Commands.Users.CreateUser;
using Cinematica.Tests.Setup.Fakers.Commands.Users.CreateUser;
using Cinematica.Tests.Setup.MockBuilders.Repositories;

namespace Cinematica.Tests.Application.Commands.Users.CreateUser;

[Trait(name: "Validator", value: "CreateUserCommand")]
public class CreateUserCommandValidatorTest()
{
    [Fact(DisplayName = "ValidateAsync() - Success case: all command object properties are valid")]
    public async Task ValidateAsync_PassUserCommandWithValidData_ValidationShouldSucceed()
    {
        // Arrange:
        var command = CreateUserCommandFake.Valid();

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupExistsAsync()
            .Build();

        var createUserCommandValidator = new CreateUserCommandValidator(userRepository);

        // Act:
        var sut = await createUserCommandValidator.ValidateAsync(command);

        // Assert:
        Assert.NotNull(sut);
        Assert.IsType<ValidationResult>(sut);
        Assert.True(sut.IsValid);
        Assert.Empty(sut.Errors);
    }

    #region Failure Cases

    [Fact(DisplayName = "ValidateAsync() - Failure case: User already exists")]
    public async Task ValidateAsync_UserAlreadyExists_ValidationShouldFail()
    {
        // Arrange:
        var command = CreateUserCommandFake.Valid();

        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupExistsAsync(exists: true)
            .Build();

        var createUserCommandValidator = new CreateUserCommandValidator(userRepository);

        // Act:
        var sut = await createUserCommandValidator.ValidateAsync(command);

        // Assert:
        Assert.NotNull(sut);
        Assert.IsType<ValidationResult>(sut);
        Assert.False(sut.IsValid);
        Assert.NotEmpty(sut.Errors);
    }

    [Theory(DisplayName = "ValidateAsync() - Failure cases: Command object properties have invalid values")]
    [ClassData(typeof(CreateUserCommandFake))]
    public async Task ValidateAsync_PassCommandObjectWithInvalidData_ValidationShouldFail(CreateUserCommand command)
    {
        // Arrange:
        var userRepository = UserRepositoryMockBuilder
            .Create()
            .SetupExistsAsync()
            .Build();

        var createUserCommandValidator = new CreateUserCommandValidator(userRepository);

        // Act:
        var sut = await createUserCommandValidator.ValidateAsync(command);

        // Assert:
        Assert.NotNull(sut);
        Assert.IsType<ValidationResult>(sut);
        Assert.False(sut.IsValid);
        Assert.NotEmpty(sut.Errors);
    }

    #endregion
}

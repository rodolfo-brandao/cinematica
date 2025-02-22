using System.Net.Mail;
using MovieLibrary.Core.Contracts.Repositories;

namespace MovieLibrary.Application.Commands.Users.CreateUser;

public class CreateUserCommandValidator : AbstractValidator<CreateUserCommand>
{
    private const byte UsernameMinLength = 3;
    private const byte UsernameMaxLength = 50;
    private const byte EmailMaxLength = 255;
    private const byte PasswordMinLength = 8;

    public CreateUserCommandValidator(IUserRepository userRepository)
    {
        RuleFor(command => command.Username)
            .NotEmpty()
            .WithMessage("The username cannot be empty, null or whitespace.")
            .MustAsync(async (username, _) =>
                !await userRepository.ExistsAsync(user => user.Username.Equals(username) && !user.IsDisabled))
            .WithMessage(command => $"User with username '{command.Username}' already exists.");

        When(command => command.Username is not null, () =>
        {
            RuleFor(command => command.Username.Length)
                .InclusiveBetween(from: UsernameMinLength, to: UsernameMaxLength)
                .WithMessage($"The username must be between {UsernameMinLength} and {UsernameMaxLength} characters.");
        });

        RuleFor(command => command.Email)
            .NotEmpty()
            .WithMessage("The e-mail cannot be empty, null or whitespace.")
            .MaximumLength(maximumLength: EmailMaxLength)
            .WithMessage($"The e-mail must not exceed {EmailMaxLength} characters.")
            .Must(email => MailAddress.TryCreate(email, out _))
            .WithMessage("The e-mail address is not valid.")
            .MustAsync(async (email, _) =>
                !await userRepository.ExistsAsync(user => user.Email.Equals(email) && !user.IsDisabled))
            .WithMessage(command => $"User with e-mail '{command.Email}' already exists.");

        RuleFor(command => command.Password)
            .NotEmpty()
            .WithMessage("The password cannot be empty, null or whitespace")
            .MinimumLength(minimumLength: PasswordMinLength)
            .WithMessage($"The password must have at least {PasswordMinLength} characters.");
    }
}
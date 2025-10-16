using Cinematica.Core.Contracts.Repositories;

namespace Cinematica.Application.Commands.Countries.CreateCountry;

public class CreateCountryCommandValidator : AbstractValidator<CreateCountryCommand>
{
    private const byte MinNameLength = 3;
    private const byte MaxNameLength = 50;
    private const string IsoAlpha3CodeRegexPattern = @"^[a-zA-Z]{3}$";

    public CreateCountryCommandValidator(ICountryRepository countryRepository)
    {
        RuleFor(command => command.Name)
            .NotEmpty()
            .WithMessage("The country name cannot be empty, null or whitespace.")
            .MustAsync(async (name, _) =>
                !await countryRepository.ExistsAsync(country => country.Name.Equals(name) && !country.IsDisabled))
            .WithMessage(command => $"Country with name '{command.Name}' already exists.");

        When(command => command.Name is not null, () =>
        {
            RuleFor(command => command.Name.Length)
                .InclusiveBetween(from: MinNameLength, to: MaxNameLength)
                .WithMessage($"The country name must be between {MinNameLength} and {MaxNameLength} characters.");
        });

        RuleFor(command => command.IsoAlpha3Code)
            .NotEmpty()
            .WithMessage("The country code cannot be empty, null or whitespace.")
            .Matches(IsoAlpha3CodeRegexPattern)
            .WithMessage("The country code must contain exactly 3 letters.")
            .MustAsync(async (code, _) =>
                !await countryRepository.ExistsAsync(country => country.IsoAlpha3Code.Equals(code) && !country.IsDisabled))
            .WithMessage(command => $"Country with code '{command.IsoAlpha3Code}' already exists.");
    }
}

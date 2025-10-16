using System.Text.Json.Serialization;

namespace Cinematica.Application.Responses.Countries;

public class CreatedCountryResponse
{
    public Guid Id { get; init; }
    public string Name { get; init; }

    [JsonPropertyName(name: "code")]
    public string IsoAlpha3Code { get; init; }

    public string CreatedOn { get; init; }
}

using Cinematica.Application.Responses.Countries;
using Cinematica.Application.Utils;
using System.Text.Json.Serialization;

namespace Cinematica.Application.Commands.Countries.CreateCountry;

public class CreateCountryCommand : IRequest<ApiResult<CreatedCountryResponse>>
{
    public string Name { get; init; }

    [JsonPropertyName("code")]
    public string IsoAlpha3Code { get; init; }
}

using Cinematica.Application.Utils;

namespace Cinematica.Application.Commands.Countries.DeleteCountry;

public class DeleteCountryCommand(Guid id) : IRequest<ApiResult<Unit>>
{
    public Guid Id { get; init; } = id;
}

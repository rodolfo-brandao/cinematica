using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Contracts.Units;
using Cinematica.Core.Models.Nulls;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Application.Commands.Countries.DeleteCountry;

public class DeleteCountryHandler(ICountryRepository countryRepository, IUnitOfWork unitOfWork)
    : IRequestHandler<DeleteCountryCommand, ApiResult<Unit>>
{
    public async Task<ApiResult<Unit>> Handle(DeleteCountryCommand request, CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<Unit>(statusCode: StatusCodes.Status204NoContent);
        var country = await countryRepository.GetByKeyAsync(request.Id) ?? new NullCountry();

        if (country is NullCountry)
        {
            apiResult.StatusCode = StatusCodes.Status404NotFound;
            apiResult.ErrorMessage = "Country not found.";
        }
        else
        {
            _ = countryRepository.Remove(country);
            _ = await unitOfWork.SaveChangesAsync();
        }

        return apiResult;
    }
}

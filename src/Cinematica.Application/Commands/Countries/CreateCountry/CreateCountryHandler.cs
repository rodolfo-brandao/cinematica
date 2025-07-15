using Cinematica.Application.Responses.Countries;
using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Factories;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Contracts.Units;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Application.Commands.Countries.CreateCountry;

public class CreateCountryHandler(
    ICountryRepository countryRepository,
    IModelFactory modelFactory,
    IUnitOfWork unitOfWork)
    : IRequestHandler<CreateCountryCommand, ApiResult<CreatedCountryResponse>>
{
    public async Task<ApiResult<CreatedCountryResponse>> Handle(CreateCountryCommand request, CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<CreatedCountryResponse>(statusCode: StatusCodes.Status201Created);
        var validationResult = await new CreateCountryCommandValidator(countryRepository)
            .ValidateAsync(request, cancellationToken);

        if (validationResult.IsValid)
        {
            var country = modelFactory.CreateCountry(request.Name, request.IsoAlpha3Code);
            var createdCountry = await countryRepository.InsertAsync(country);
            _ = await unitOfWork.SaveChangesAsync();
            apiResult.Response = new CreatedCountryResponse
            {
                Id = createdCountry.Id,
                Name = createdCountry.Name,
                IsoAlpha3Code = createdCountry.IsoAlpha3Code,
                CreatedOn = createdCountry.CreatedOn.ToString(format: "yyyy-MM-dd HH:mm:ss") + " UTC"
            };
        }
        else
        {
            apiResult.StatusCode = (int)HttpStatusCode.BadRequest;
            apiResult.ErrorMessage = validationResult.Errors.First().ErrorMessage;
        }

        return apiResult;
    }
}

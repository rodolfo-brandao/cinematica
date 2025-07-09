using Microsoft.AspNetCore.Mvc;

namespace Cinematica.Application.Utils.QueryTools.Abstract;

/// <summary>
/// Centralizes and exposes basic paging and sorting properties to be used as query params in HTTP requests.
/// </summary>
public abstract class BaseQueryParams : IPaging, ISorting
{
    [FromQuery(Name = "page")]
    public int Page { get; set; } = 1;

    [FromQuery(Name = "size")]
    public int PageSize { get; set; } = 10;

    [FromQuery(Name = "direction")]
    public string Direction { get; set; } = "asc";

    [FromQuery(Name = "sort")]
    public string SortBy { get; set; } = string.Empty;
}

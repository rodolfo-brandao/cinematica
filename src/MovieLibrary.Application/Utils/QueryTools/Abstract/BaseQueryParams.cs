using Microsoft.AspNetCore.Mvc;

namespace MovieLibrary.Application.Utils.QueryTools.Abstract;

/// <summary>
/// Provides basic properties to be used as query params in HTTP requests for paging and sorting.
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
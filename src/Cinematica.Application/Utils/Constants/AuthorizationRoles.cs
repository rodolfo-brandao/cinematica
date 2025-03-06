namespace Cinematica.Application.Utils.Constants;

/// <summary>
/// A set of constants related to roles that are used to authorize API requests.
/// </summary>
public static class AuthorizationRoles
{
    public const string Admin = "admin";
    public const string AdminUser = "admin,user";
    public const string User = "user";
}

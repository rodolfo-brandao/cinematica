using Cinematica.Core.Models;

namespace Cinematica.Core.Contracts.Services;

/// <summary>
/// A service specialized on managing passwords and JSON Web Tokens.
/// </summary>
public interface ISecurityService
{
    /// <summary>
    /// Creates a 128-bit hash value from the given raw password,
    /// which is fed with a newly generated salt, using the MD5 algorithm.
    /// </summary>
    /// <param name="rawPassword">The raw string representing the password.</param>
    /// <returns>A tuple of strings containing the newly created password and salt hashes.</returns>
    (string PasswordHash, string PasswordSalt) CreatePasswordHash(string rawPassword);

    /// <summary>
    /// Issues a JSON Web Token (JWT) based on the given user role.
    /// </summary>
    /// <param name="user">The respective user to have the access token created based on their access level.</param>
    /// <param name="expirationTime">The duration at which the token should expire, preferably in UTC.</param>
    /// <returns>A <see langword="string"/> representing the newly created JSON Web Token (JWT).</returns>
    /// <exception cref="NullReferenceException">The JWT secret was not found or does not exist.</exception>
    string CreateJsonWebToken(User user, TimeOnly expirationTime);

    /// <summary>
    /// Validates whether the given raw password matches the hash and salt of another one.
    /// </summary>
    /// <param name="rawPassword">The raw password provided by a user.</param>
    /// <param name="passwordHash">The hash of an existing password.</param>
    /// <param name="passwordSalt">The salt hash of the existing password.</param>
    /// <returns><see langword="true"/> if the given raw password matches the given hash and salt. Otherwise, <see langword="false"/>.</returns>
    bool ValidatePassword(string rawPassword, string passwordHash, string passwordSalt);
}

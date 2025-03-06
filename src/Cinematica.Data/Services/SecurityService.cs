using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using Cinematica.Core.Contracts.Services;
using Cinematica.Core.Models;
using Cinematica.Data.Extensions;

namespace Cinematica.Data.Services;

public class SecurityService(IConfiguration configuration) : ISecurityService
{
    private const string HexadecimalStringFormat = "x2";

    public (string PasswordHash, string PasswordSalt) CreatePasswordHash(string rawPassword)
    {
        var salt = CreateSalt();
        return (CreateHash(rawPassword, salt), salt);
    }

    public string CreateJsonWebToken(User user, TimeOnly expirationTime)
    {
        var jwtSecret = configuration.GetSection(key: "Jwt:Secret").Value;

        if (jwtSecret is null)
        {
            throw new NullReferenceException("The JWT secret was not found or does not exist.");
        }

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret));
        var signInCredentials = new SigningCredentials(key, algorithm: SecurityAlgorithms.HmacSha512Signature);

        var claims = new List<Claim>
        {
            new(type: ClaimTypes.Name, user.Id.ToString()),
            new(type: ClaimTypes.Role, user.Role)
        };

        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(claims),
            Expires = DateTime.UtcNow + expirationTime.ToTimeSpan(),
            SigningCredentials = signInCredentials
        };

        var tokenHandler = new JwtSecurityTokenHandler();
        var securityToken = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(securityToken);
    }

    public bool ValidatePassword(string rawPassword, string passwordHash, string passwordSalt)
    {
        return CreateHash(rawPassword, passwordSalt).Equals(passwordHash);
    }

    #region Private Methods

    private static string CreateHash(string rawPassword, string salt)
    {
        var bytes = MD5.HashData(source: Encoding.UTF8.GetBytes(s: $"{rawPassword}{salt}"));
        return bytes.ParseToString(format: HexadecimalStringFormat);
    }

    private static string CreateSalt(int size = 12)
    {
        using var randomNumberGenerator = RandomNumberGenerator.Create();
        var bytes = new byte[size];
        randomNumberGenerator.GetBytes(bytes);
        return bytes.ParseToString(format: HexadecimalStringFormat);
    }

    #endregion
}

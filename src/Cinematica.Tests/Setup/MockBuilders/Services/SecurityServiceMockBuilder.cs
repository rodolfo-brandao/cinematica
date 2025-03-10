using Cinematica.Core.Contracts.Services;
using Cinematica.Tests.Setup.MockBuilders.Abstract;

namespace Cinematica.Tests.Setup.MockBuilders.Services;

/// <summary>
/// A builder to expose mock functionalities of <see cref="ISecurityService"/>.
/// </summary>
internal sealed class SecurityServiceMockBuilder : BaseMockBuilder<SecurityServiceMockBuilder, ISecurityService>
{
    /// <summary>
    /// Mocks the 'CreatePasswordHash()' method.
    /// </summary>
    /// <param name="passwordHash">The hash to represent the encrypted raw password.</param>
    /// <param name="passwordSalt">The random character sequence to be used as salt in the password.</param>
    /// <returns>The <see cref="SecurityServiceMockBuilder"/> so that additional calls can be chained.</returns>
    public SecurityServiceMockBuilder SetupCreatePasswordHash(string passwordHash, string passwordSalt)
    {
        Mock.Setup(service => service.CreatePasswordHash(It.IsAny<string>())).Returns((passwordHash, passwordSalt));
        return this;
    }

    /// <summary>
    /// Mocks the 'ValidatePassword()' method.
    /// </summary>
    /// <param name="isValid">Defines when the method should indicate whether the password is valid or not.</param>
    /// <returns>The <see cref="SecurityServiceMockBuilder"/> so that additional calls can be chained.</returns>
    public SecurityServiceMockBuilder SetupValidatePassword(bool isValid = true)
    {
        Mock.Setup(service => service.ValidatePassword(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
            .Returns(isValid);
        return this;
    }
}
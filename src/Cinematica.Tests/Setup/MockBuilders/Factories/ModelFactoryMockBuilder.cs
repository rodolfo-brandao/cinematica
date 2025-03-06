using Cinematica.Core.Contracts.Factories;
using Cinematica.Tests.Setup.Fakers.Models;
using Cinematica.Tests.Setup.MockBuilders.Abstract;

namespace Cinematica.Tests.Setup.MockBuilders.Factories;

/// <summary>
/// A builder to expose mock functionalities of <see cref="IModelFactory"/>.
/// </summary>
internal sealed class ModelFactoryMockBuilder : BaseMockBuilder<ModelFactoryMockBuilder, IModelFactory>
{
    /// <summary>
    /// Mocks the 'CreateUser()' method.
    /// </summary>
    /// <returns>The <see cref="ModelFactoryMockBuilder"/> so that additional calls can be chained.</returns>
    public ModelFactoryMockBuilder SetupCreateUser()
    {
        Mock.Setup(factory => factory.CreateUser(
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>(),
            It.IsAny<string>())).Returns(UserFake.Valid());
        return this;
    }
}
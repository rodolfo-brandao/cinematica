using MovieLibrary.Core.Contracts.Factories;
using MovieLibrary.Tests.Setup.Fakers.Models;
using MovieLibrary.Tests.Setup.MockBuilders.Abstract;

namespace MovieLibrary.Tests.Setup.MockBuilders.Factories;

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
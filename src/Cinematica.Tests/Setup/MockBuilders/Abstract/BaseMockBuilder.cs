namespace Cinematica.Tests.Setup.MockBuilders.Abstract;

/// <summary>
/// Abstract base class to centralize reusable methods and properties across all mock builders.
/// </summary>
/// <typeparam name="TMockBuilder">The type of the respective mock builder.</typeparam>
/// <typeparam name="TMockTarget">The type of the class/interface to have its methods mocked.</typeparam>
internal abstract class BaseMockBuilder<TMockBuilder, TMockTarget>
    where TMockBuilder : class, new()
    where TMockTarget : class
{
    /// <summary>
    /// Exposes an instance of the respective mock.
    /// </summary>
    protected readonly Mock<TMockTarget> Mock = new();

    /// <summary>
    /// Exposes an instance of the type mocked by the builder.
    /// </summary>
    /// <returns>An instance of <see cref="TMockTarget"/>.</returns>
    public TMockTarget Build() => Mock.Object;

    /// <summary>
    /// Initializes an instance of the mock builder.
    /// </summary>
    /// <returns>An instance of <see cref="TMockBuilder"/>.</returns>
    public static TMockBuilder Create() => new();
}

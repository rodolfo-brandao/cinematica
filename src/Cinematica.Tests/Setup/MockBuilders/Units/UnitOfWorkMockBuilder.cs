using Cinematica.Core.Contracts.Units;
using Cinematica.Tests.Setup.MockBuilders.Abstract;

namespace Cinematica.Tests.Setup.MockBuilders.Units;

/// <summary>
/// A builder to expose mock functionalities of <see cref="IUnitOfWork"/>.
/// </summary>
internal sealed class UnitOfWorkMockBuilder : BaseMockBuilder<UnitOfWorkMockBuilder, IUnitOfWork>
{
    /// <summary>
    /// Mocks the 'SaveChangesAsync()' method.
    /// </summary>
    /// <returns>The <see cref="UnitOfWorkMockBuilder"/> so that additional calls can be chained.</returns>
    public UnitOfWorkMockBuilder SetupSaveChangesAsync()
    {
        Mock.Setup(unitOfWork => unitOfWork.SaveChangesAsync()).ReturnsAsync(byte.MinValue);
        return this;
    }
}
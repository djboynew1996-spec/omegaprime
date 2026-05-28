using System;
using System.Threading;
using System.Threading.Tasks;
using Xunit;
using OmegaPrime.Production;

namespace OmegaPrime.Tests
{
    public class SecurityValidatorTests
    {
        [Theory]
        [InlineData("Hello World", true)]
        [InlineData("Analyze this data", true)]
        [InlineData("DROP TABLE users", false)]
        [InlineData("<script>alert('xss')</script>", false)]
        [InlineData("", false)]
        [InlineData(null, false)]
        public void IsValidInput_ValidatesCorrectly(string input, bool expected)
        {
            var result = SecurityValidator.IsValidInput(input);
            Assert.Equal(expected, result);
        }

        [Fact]
        public void GenerateLicense_CreatesValidFormat()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            
            var license = SecurityValidator.GenerateLicense("test-customer", DateTime.UtcNow.AddDays(30));
            
            Assert.StartsWith("OMEGA-", license);
            Assert.Contains("-", license);
        }

        [Fact]
        public void ValidateLicense_AcceptsValidLicense()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            
            var expiry = DateTime.UtcNow.AddDays(30);
            var license = SecurityValidator.GenerateLicense("test-customer", expiry);
            
            var isValid = SecurityValidator.ValidateLicense(license, out var customerId, out var expiryDate);
            
            Assert.True(isValid);
            Assert.Equal("test-customer", customerId);
            Assert.True(expiryDate > DateTime.UtcNow);
        }

        [Fact]
        public void ValidateLicense_RejectsExpiredLicense()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            
            var expiry = DateTime.UtcNow.AddDays(-1); // Expired
            var license = SecurityValidator.GenerateLicense("test-customer", expiry);
            
            var isValid = SecurityValidator.ValidateLicense(license, out _, out _);
            
            Assert.False(isValid);
        }

        [Fact]
        public void ValidateLicense_RejectsTamperedLicense()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            
            var license = SecurityValidator.GenerateLicense("test-customer", DateTime.UtcNow.AddDays(30));
            var tamperedLicense = license.Replace('A', 'B'); // Tamper with license
            
            var isValid = SecurityValidator.ValidateLicense(tamperedLicense, out _, out _);
            
            Assert.False(isValid);
        }
    }

    public class OmegaNodeTests
    {
        [Fact]
        public void Constructor_InitializesCorrectly()
        {
            var node = new OmegaNode(50.0);
            
            Assert.Equal(50.0, node.SkillLevel);
            Assert.Equal(1.0, node.EnergyEfficiency);
            Assert.Equal(AgentState.Dormant, node.State);
        }

        [Fact]
        public void Constructor_ClampsSkillLevel()
        {
            var node1 = new OmegaNode(-10.0);
            var node2 = new OmegaNode(200.0);
            
            Assert.Equal(1.0, node1.SkillLevel);
            Assert.Equal(100.0, node2.SkillLevel);
        }

        [Fact]
        public void Evolve_IncreasesSkillLevel()
        {
            var node = new OmegaNode(50.0);
            var initialSkill = node.SkillLevel;
            
            node.Evolve(1);
            
            Assert.True(node.SkillLevel > initialSkill);
            Assert.Equal(AgentState.Transcending, node.State);
        }

        [Fact]
        public async Task ProcessRealityAsync_ReturnsValidResult()
        {
            var node = new OmegaNode(50.0);
            using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
            
            var result = await node.ProcessRealityAsync("test input", 60.0, cts.Token);
            
            Assert.NotNull(result);
            Assert.Contains("Node-", result);
            Assert.Contains("Skill:", result);
        }

        [Fact]
        public async Task ProcessRealityAsync_ThrowsOnNullInput()
        {
            var node = new OmegaNode(50.0);
            using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
            
            await Assert.ThrowsAsync<ArgumentException>(() => 
                node.ProcessRealityAsync(null, 60.0, cts.Token));
        }

        [Fact]
        public async Task ProcessRealityAsync_HandlesCancellation()
        {
            var node = new OmegaNode(50.0);
            using var cts = new CancellationTokenSource();
            cts.Cancel(); // Cancel immediately
            
            var result = await node.ProcessRealityAsync("test", 60.0, cts.Token);
            
            Assert.Contains("TIMEOUT", result);
        }
    }

    public class RateLimiterTests
    {
        [Fact]
        public void TryAcquire_AllowsUpToLimit()
        {
            var limiter = new RateLimiter(5);
            
            for (int i = 0; i < 5; i++)
            {
                Assert.True(limiter.TryAcquire());
            }
            
            Assert.False(limiter.TryAcquire()); // 6th should fail
        }

        [Fact]
        public async Task TryAcquire_ResetsAfterTimeWindow()
        {
            var limiter = new RateLimiter(2);
            
            Assert.True(limiter.TryAcquire());
            Assert.True(limiter.TryAcquire());
            Assert.False(limiter.TryAcquire());
            
            await Task.Delay(61000); // Wait for time window to reset
            
            Assert.True(limiter.TryAcquire());
        }
    }

    public class ConsciousnessCoreTests
    {
        [Fact]
        public void Constructor_ThrowsOnInvalidLicense()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            
            Assert.Throws<UnauthorizedAccessException>(() => 
                new ConsciousnessCore("INVALID-LICENSE"));
        }

        [Fact]
        public void Constructor_AcceptsValidLicense()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            Environment.SetEnvironmentVariable("OMEGA_DB_PATH", "./test_omega_data.json");
            
            var license = SecurityValidator.GenerateLicense("test", DateTime.UtcNow.AddDays(30));
            var core = new ConsciousnessCore(license);
            
            Assert.NotNull(core);
        }

        [Fact]
        public async Task WeaveRealityAsync_RejectsDangerousInput()
        {
            Environment.SetEnvironmentVariable("OMEGA_SECRET_KEY", "TestSecretKey123");
            Environment.SetEnvironmentVariable("OMEGA_DB_PATH", "./test_omega_data.json");
            
            var license = SecurityValidator.GenerateLicense("test", DateTime.UtcNow.AddDays(30));
            var core = new ConsciousnessCore(license);
            core.Awaken(10);
            
            var result = await core.WeaveRealityAsync("DROP TABLE users");
            
            Assert.Contains("ERROR", result);
        }
    }
}

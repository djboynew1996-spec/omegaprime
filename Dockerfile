# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY *.csproj ./
RUN dotnet restore

COPY . ./
RUN dotnet publish -c Release -o /app/publish

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/runtime:10.0 AS runtime
WORKDIR /app

# Security: Run as non-root user
RUN useradd -m -u 1000 omega && \
    chown -R omega:omega /app
USER omega

COPY --from=build /app/publish .

# Environment variables (override with -e or .env)
ENV OMEGA_SECRET_KEY=""
ENV OMEGA_DB_PATH="/app/data/omega_data.json"
ENV OMEGA_MAX_CONCURRENT="50"
ENV OMEGA_RATE_LIMIT="60"

# Create data directory
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD test -f /app/omega.log || exit 1

ENTRYPOINT ["dotnet", "OmegaPrime.dll"]

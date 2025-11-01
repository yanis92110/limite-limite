# Utilise une image Java avec Maven préinstallé
FROM maven:3.9.2-eclipse-temurin-17 AS build

WORKDIR /app

# Copier les fichiers Maven et le code source
COPY pom.xml .
COPY src ./src

# Compiler le projet
RUN mvn clean package -DskipTests

# Utiliser une image Java plus légère pour lancer le jar
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# Copier le jar depuis l'image build
COPY --from=build /app/target/jeu-cartes-pwa-1.0-jar-with-dependencies.jar app.jar

# Exposer le port
EXPOSE 8080

# Commande pour lancer l'application
CMD ["java", "-jar", "app.jar"]

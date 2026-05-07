from coloranalysis.ai.region_extraction import RegionExtractionService

service = RegionExtractionService()
result = service.extract_regions("1.jpeg")

print(result)
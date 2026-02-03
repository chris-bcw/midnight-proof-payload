# create output directory if it doesn't exist
mkdir -p out

# take URL in argument or use default
URL=${1:-'http://127.0.0.1:6300'}

curl -X POST "$URL/check" --data-binary '@check-payload.bin' --output out/check-response.bin

echo "Response saved to out/check-response.bin"

#  print hex dump of response
hexdump -C out/check-response.bin | head -20
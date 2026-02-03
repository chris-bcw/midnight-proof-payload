# create output directory if it doesn't exist
mkdir -p out

# take URL in argument or use default
URL=${1:-'http://127.0.0.1:6300'}

curl -X POST "$URL/prove" --data-binary '@prove-b-payload.bin' --output out/prove-b-response.bin

echo "Response saved to out/prove-b-response.bin"

#  print hex dump of response
hexdump -C out/prove-b-response.bin | head -20
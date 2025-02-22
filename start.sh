function auto() {
    python3 auto_proxy.py proxy_list.txt
    sleep 10
    echo -e "1\n2oEErIJMp0gNXJVfshOf7PtnjUx" | python3 run.py &
    GRASS_PID=$!
    echo "grass_desktop.py running with PID: $GRASS_PID"
}
function stop_grass() {
    if [ ! -z "$GRASS_PID" ]; then
        echo "Stopping grass_desktop.py with PID: $GRASS_PID"
        kill -9 $GRASS_PID
    else
        echo "No grass_desktop.py process found to stop."
    fi
}
while true; do
    echo "Starting auto process..."
    auto
    sleep 600
    stop_grass
done

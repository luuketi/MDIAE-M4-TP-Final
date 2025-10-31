# MDIAE - M4 - Lenguajes y sistemas operativos de aplicación espacial.

## Trabajo Práctico Final

### Dependencias
* python
* pandas
* seaborn
* plotly

### Instalar dependencias

```bash
make install
```

### Ejecución

```bash
make run CGSS_20150603_091700_10020150603085920_SACD_HKTMST.bin
```

 > [!NOTE]
 >
 > La posición del campo ```timestamp``` (**598**) fue determinada con el siguente script:
 > ```python
>  import struct
>  from collections import defaultdict
>  from datetime import datetime
>  
>  
>  PACKET_SIZE = 4000
>  
>  
>  def read_timestamp(position):
>      timestamp_raw = packets[position: position + 4]
>      timestamp = struct.unpack("<L", timestamp_raw)[0]
>      return datetime.fromtimestamp(timestamp)
>  
>  
>  packets = open('CGSS_20150603_091700_10020150603085920_SACD_HKTMST.bin', 'rb').read()
>  
>  number_of_packets = len(packets) // PACKET_SIZE
>  print(f"Number of packets: {number_of_packets}")
>  
>  timestamps = defaultdict(set)
>  for offset in range(0, PACKET_SIZE - 3):
>      for position in range(0, len(packets), PACKET_SIZE):
>          datetime_ = read_timestamp(position + offset)
>          if datetime(2000, 1, 1) < datetime_ < datetime(2025, 1, 1):
>              timestamps[offset].add(datetime_)
>  
>  out = open('timestamps.txt', 'w')
>  for offset, timestamps_ in timestamps.items():
>      if len(timestamps_) == number_of_packets:
>          out.write(f"Offset: {offset}, Datetimes: {sorted(timestamps_)}\n")
>  ```
>
> La posición **598** (4 bytes big-endian) contiene valores similares (con diferencia de algunos segundos) a la posición **100** (4 bytes little-endian)
> 

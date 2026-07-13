#!/bin/bash
echo accession"|"organism"|"country"|"host"|"isolation_source"|"size > metadata.txt
while read line
do {
	accession=$(echo ${line} | sed 's/.txt//')
	organism=$(cat plasmid_genbank/"${line}" | egrep 'ORGANISM' | tr ' ' '-' | sed "s/--/ /" | sed "s/--/ /" | awk '{print $2}' | tr '-' ' ')
	locatie=$(cat plasmid_genbank/"${line}" | egrep 'geo_loc_name' | tr '=:"' ' ' | awk '{print $2}')
	host=$(cat plasmid_genbank/"${line}" | egrep '/host=' | tr '="' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}')
	isolation_source=$(cat plasmid_genbank/"${line}" | egrep '/isolation_source=' | tr '="' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}')
	size=$(cat plasmid_genbank/"${line}" | egrep 'LOCUS' | awk '{print $3}')
	echo ${accession}'|'${organism}'|'${geoloc}'|'${host}'|'${isolation_source}'|'${size}  >> metadata.txt
	echo "$accession  $organism  $locatie  $host  $isolation_source  $size" 
}
done < metadata_list.txt

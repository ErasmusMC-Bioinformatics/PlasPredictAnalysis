#nieuwe genbank collector
#!/bin/bash
echo accession"|"host"|"locatie"|"size > metadata.txt
while read line
do {
	#cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'geo_loc_name' | tr '=' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}' | tr ':' ' ' | awk '{print $1}' 
	organism=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'ORGANISM' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}')
	accession=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'VERSION' | awk '{print $2}')
	size=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'LOCUS' | awk '{print $3}')
        geo_loc=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'geo_loc_name' | tr '="' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}')
	geoloc=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'geo_loc_name' | tr '=' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}' | tr ':' ' ' | awk '{print $1}' | tr -d '"')
	mol_type=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'mol_type' | tr '="' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}')
        host=$(cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep '/host=' | tr '="' ' ' | awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}')
        echo ${accession}'|'${host}'|'${geoloc}'|'${size}  >> metadata.txt
	echo ${geoloc} >> incx4_countries.txt
	cat /mnt/DATAPOOL/mmibstudent2/Plasmid_project/plasmid_collection/plasmid_genbank/${line} | egrep 'geo_loc_name'  | tr " " "-" | tr "=" " " |  awk '{for (i=2;i<=NF;i++) printf $i (i<NF?OFS:ORS)}' | tr ':' ' ' | awk '{print $1}' | tr -d '"' 
 
}
done < genbankfiles.txt

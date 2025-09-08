#include <assignment2.h>

int32_t main(int32_t argc, char *argv[])
{
	int32_t fd;

	if(argc!=2) {
		printf("Usage: editro <file>\n");
		return 0;
	}

	fd = open(argv[1], O_RDWR|O_SYNC);
	if(fd<0) {
		printf("Error %d Unable to open %s\n", fd, argv[1]);
		return 0;
	}

	Elf64_Ehdr ehdr;
	Elf64_Shdr* sh_tbl;
	
	read_elf_header(fd, &ehdr);
	
    if(!is_elf(ehdr)) {
		return 0;
	}
	puts("ELF");

	sh_tbl = malloc(ehdr.e_shentsize * ehdr.e_shnum);
	if(!sh_tbl) {
		printf("Failed to allocate %d bytes\n", (ehdr.e_shentsize * ehdr.e_shnum));
	}
	print_section_headers(fd, ehdr, sh_tbl);

	free(sh_tbl);
	

	return 0;

}


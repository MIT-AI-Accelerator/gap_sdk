# LICENCE: GPLv2 (see COPYING)
# Copyright Greenwaves Technologies 2019
# Author: Antoine Faravelon (antoine.faravelon@greenwaves-technologies.com)

# comm struct
#  ____________________
# |    Content  | Size |
# |------0------|------|
# | HOST RDY    | (4)  |
# |-----+4------|------|
# | GAP RDY     | (4)  |
# |-----+8------|------|
# | Buff ptr    | (4)  |
# |-----+12-----|------|
# | Buff Size   | (4)  |
# |-----+16-----|------| --- 
# | FLASH RUN   | (4)  | # for flasher only
# |-----+20-----|------|
# | FLASH_ADDR  | (4)  | 
# |-----+24-----|------|
# | FLASH_SIZE  | (4)  |
# |-----+28-----|------|
# | FLASH_TYPE  | (4)  |
# |_____________|______|

# Flash types:
# HYPERFLASH = 0
# SPI FLASH  = 1

# gap flasher ctrl: load a bin ImageName of size ImageSize to flash at addr 0x0+flash_offset
proc gap_flasher_ctrl {ImageName ImageSize flash_offset sector_size flash_type device_struct_ptr_addr} {
    # set pointers to right addresses
    set count [expr 0x0]
    mem2array device_struct_ptr 32 $device_struct_ptr_addr 1
    while { [expr (($device_struct_ptr(0) == 0xdeadbeef)\
            || ($device_struct_ptr(0) == 0x0)) && ($count < 0x80)] } {
        mem2array device_struct_ptr 32 $device_struct_ptr_addr 1
        sleep 100
        set count [expr $count + 0x1]
    }
    if { [expr $count == 0x80] } {
        puts "flasher script could not connect to board, check your cables"
        exit
    }
    puts "device struct address is $device_struct_ptr(0)"
    set host_rdy        [expr $device_struct_ptr(0) + 0 ]
    set gap_rdy         [expr $device_struct_ptr(0) + 4 ]
    set buff_ptr_addr   [expr $device_struct_ptr(0) + 8 ]
    set buff_size_addr  [expr $device_struct_ptr(0) + 12 ]
    set flash_run       [expr $device_struct_ptr(0) + 16 ]
    set flash_addr      [expr $device_struct_ptr(0) + 20 ]
    set flash_size      [expr $device_struct_ptr(0) + 24 ]
    set flash_type_addr [expr $device_struct_ptr(0) + 28 ]
    set size            [expr $ImageSize]
    # rest synchronisation vars
    # GAP RDY  <--- 0
    mww [expr $gap_rdy] 0x0
    mww [expr $flash_type_addr] [expr $flash_type]
    # tell the chip we are going to flash
    mww [expr $flash_run] 0x1
    # HOST RDY <--- 1 / signal to begin app
    mww [expr $host_rdy] 0x1
    mem2array buff_ptr 32 $buff_ptr_addr 1
    set curr_offset [expr 0]
    puts "going to wait on addr GAP_RDY"
    while { $size > 0 } {
    if { $size > $sector_size } {
            set curr_size [expr $sector_size]
            set size [expr $size - $sector_size]
        } else {
            set curr_size [expr $size]
            set size [expr 0]
        }
        # spin on gap rdy: wait for current flash write to finish
        mem2array wait1 32 $gap_rdy 1
        while { [expr $wait1(0) != 1] } {
            mem2array wait1 32 $gap_rdy 1
            sleep 1
        }
        puts "wait on gap_rdy done witg buff ptr $buff_ptr"
        mww [expr $host_rdy] 0x0
        if { $size == 0 } {
            mww [expr $flash_run] 0x0
        }

        mww [expr $flash_addr] $curr_offset
        mww [expr $flash_size] $curr_size
        # Shift addr to the left, and set the normal base addr as min to throw
        # away bin we already read
    puts "loading image with addr [expr $buff_ptr(0) - $curr_offset] addr_min $buff_ptr(0) and size $curr_size"
        load_image $ImageName [expr $buff_ptr(0) - $curr_offset] bin $buff_ptr(0) $curr_size
        puts "load image done"
        set curr_offset [expr $curr_offset + $curr_size]
        #signal app we wrote our buff
        # ACK the gap rdy now that we wrote sector (flasher may work)
        mww [expr $gap_rdy] 0x0
        #signal we are rdy when flasher is
        mww [expr $host_rdy] 0x1
    }
        # just ensure flasher app does not continue
    mem2array wait1 32 $flash_run 1
    while { [expr $wait1(0) != 1] } {
        mem2array wait1 32 $flash_run 1
        sleep 1
    }
    puts "flasher is done, exiting"
        mww [expr $gap_rdy]   0x0
        mww [expr $host_rdy]  0x0
}

proc gap_flasher_ctrl_VEGA {ImageName ImageSize flash_offset sector_size flash_type device_struct_ptr_addr} {
    # set pointers to right addresses
    #set count [expr 0x0]
    #mem2array device_struct_ptr 32 $device_struct_ptr_addr 1
    #while { [expr (($device_struct_ptr(0) == 0xdeadbeef)\
    #        || ($device_struct_ptr(0) == 0x0)) && ($count < 0x80)] } {
    #    mem2array device_struct_ptr 32 $device_struct_ptr_addr 1
    #    sleep 100
    #    set count [expr $count + 0x1]
    #}
    #if { [expr $count == 0x80] } {
    #    puts "flasher script could not connect to board, check your cables"
    #    exit
    #}
    #DID IT MANUALLY AS NOT SURE WHY I WAS READING A WRONG POINTER
    set device_struct_ptr(0) [expr 0x1c001b10]

    puts "device struct address is $device_struct_ptr(0)"
    set host_rdy        [expr $device_struct_ptr(0) + 0 ]
    set gap_rdy         [expr $device_struct_ptr(0) + 4 ]
    set buff_ptr_addr   [expr $device_struct_ptr(0) + 8 ]
    set buff_size_addr  [expr $device_struct_ptr(0) + 12 ]
    set flash_run       [expr $device_struct_ptr(0) + 16 ]
    set flash_addr      [expr $device_struct_ptr(0) + 20 ]
    set flash_size      [expr $device_struct_ptr(0) + 24 ]
    set flash_type_addr [expr $device_struct_ptr(0) + 28 ]
    set size            [expr $ImageSize]
    # rest synchronisation vars
    # GAP RDY  <--- 0
    #mww [expr $gap_rdy] 0x0
    mww [expr $flash_type_addr] [expr $flash_type]
    # tell the chip we are going to flash
    mww [expr $flash_run] 0x1
    # HOST RDY <--- 1 / signal to begin app
    mww [expr $host_rdy] 0x1
    # spin on gap rdy: wait for flasher to run
    puts "going to wait on addr GAP_RDY"
    mem2array wait1 32 $gap_rdy 1
    while { [expr $wait1(0) != 1] } {
        mem2array wait1 32 $gap_rdy 1
        sleep 100
    }
    mem2array buff_ptr 32 $buff_ptr_addr 1
    set curr_offset [expr 0]
    while { $size > 0 } {
    if { $size > $sector_size } {
            set curr_size [expr $sector_size]
            set size [expr $size - $sector_size]
        } else {
            set curr_size [expr $size]
            set size [expr 0]
        }
        # spin on gap rdy: wait for current flash write to finish
        mem2array wait1 32 $gap_rdy 1
        while { [expr $wait1(0) != 1] } {
            mem2array wait1 32 $gap_rdy 1
            sleep 100
        }
        puts "wait on gap_rdy done witg buff ptr $buff_ptr"
        mww [expr $host_rdy] 0x0
        if { $size == 0 } {
            mww [expr $flash_run] 0x0
        }

        mww [expr $flash_addr] $curr_offset
        mww [expr $flash_size] $curr_size
        # Shift addr to the left, and set the normal base addr as min to throw
        # away bin we already read
    puts "loading image with addr [expr $buff_ptr(0) - $curr_offset] addr_min $buff_ptr(0) and size $curr_size"
        load_image $ImageName [expr $buff_ptr(0) - $curr_offset] bin $buff_ptr(0) $curr_size
        puts "load image done"
        set curr_offset [expr $curr_offset + $curr_size]
        #signal app we wrote our buff
        # ACK the gap rdy now that we wrote sector (flasher may work)
        mww [expr $gap_rdy] 0x0
        #signal we are rdy when flasher is
        mww [expr $host_rdy] 0x1
    }
        # just ensure flasher app does not continue
    mem2array wait1 32 $flash_run 1
    while { [expr $wait1(0) != 1] } {
        mem2array wait1 32 $flash_run 1
        sleep 1
    }
    puts "flasher is done, exiting"
        mww [expr $gap_rdy]   0x0
        mww [expr $host_rdy]  0x0
}

proc gap_flash_raw {image_name image_size gap_tools_path} {
    # flash the flasher
    gap8_jtag_load_binary_and_start ${gap_tools_path}/gap_bins/gap_flasher@gapoc_a.elf elf
    sleep 100
    # flash the flash image with the flasher
    gap_flasher_ctrl $image_name $image_size 0 0x40000 0 0x1c000090
    sleep 2

    puts "--------------------------"
    puts "Reset CONFREG to 0"
    puts "--------------------------"
    reset
    # remove polling, prevent openocd from complaining while reset tap
    poll off
    irscan gap8.cpu 0x7
    drscan gap8.cpu 0x4 0x0
    # set reset signals (direct control) jtag_reset 0 1
    jtag_reset 0 0
    # exit openocd, card will boot from flash
    exit
}

proc gap_flash_raw_hyper {image_name image_size gap_tools_path} {
    # flash the flasher
    puts "--------------------------"
    puts "begining flash session (hyperflash)"
    puts "--------------------------"
    puts "load flasher to L2 memory"
    gap8_jtag_load_binary_and_start ${gap_tools_path}/gap_bins/gap_flasher@gapoc_a.elf elf
    sleep 2
    # flash the flash image with the flasher
    puts "Instruct flasher to begin flash per se"
    gap_flasher_ctrl $image_name $image_size 0 0x40000 0 0x1c000090
    sleep 2
    puts "--------------------------"
    puts "flasher is done!"
    puts "--------------------------"
    puts "--------------------------"
    puts "Reset CONFREG to 0"
    puts "--------------------------"
    reset
    # remove polling, prevent openocd from complaining while reset tap
    poll off
    irscan gap8.cpu 0x7
    drscan gap8.cpu 0x4 0x0
    # set reset signals (direct control) jtag_reset 0 1
    jtag_reset 0 0
    # exit openocd, card will boot from flash
    exit

}

# specific for gap9
# will need to adapt the same way as gap builder to 
# pass all parameters for the name
proc gap9_flash_raw_hyper {image_name image_size gap_tools_path} {
    # flash the flasher
    puts "--------------------------"
    puts "begining flash session (hyperflash)"
    puts "--------------------------"
    puts "load flasher to L2 memory"
    # need to pass board name as arg -- TODO: unify command name
    load_and_start_binary ${gap_tools_path}/gap_bins/gap_flasher@gapuino9.elf 0x1c010180
    sleep 100
    # flash the flash image with the flasher
    puts "Instruct flasher to begin flash per se"
    gap_flasher_ctrl $image_name $image_size 0 0x40000 0 0x1c010090
    sleep 2
    puts "--------------------------"
    puts "flasher is done!"
    puts "--------------------------"
}

# specific for gap9
# will need to adapt the same way as gap builder to 
# pass all parameters for the name
proc vega_flash_raw_hyper {image_name image_size gap_tools_path} {
    #redirect errors to log file
    log_output openocd.log
    # flash the flasher
    puts "--------------------------"
    puts "begining flash session (hyperflash)"
    puts "--------------------------"
    puts "load flasher to L2 memory"
    # need to pass board name as arg -- TODO: unify command name
    load_and_start_binary ${gap_tools_path}/gap_bins/gap_flasher@vega.elf 0x1c008080
    sleep 2
    # flash the flash image with the flasher
    puts "Instruct flasher to begin flash per se"
    gap_flasher_ctrl_VEGA $image_name $image_size 0 0x40000 0 0x1c008090
    sleep 2
    puts "--------------------------"
    puts "flasher is done!"
    puts "--------------------------"
}

proc gap_flash_raw_spi {image_name image_size gap_tools_path} {
    # flash the flasher
    puts "--------------------------"
    puts "begining flash session (spiflash)"
    puts "--------------------------"
    puts "load flasher to L2 memory"
    gap8_jtag_load_binary_and_start ${gap_tools_path}/gap_bins/gap_flasher@gapoc_a_qpif.elf elf
    sleep 2
    # flash the flash image with the flasher
    puts "Instruct flasher to begin flash per se"
    gap_flasher_ctrl $image_name $image_size 0 0x1000 1 0x1c000090
    sleep 2
    puts "--------------------------"
    puts "flasher session is done!"
    puts "--------------------------"
    puts "--------------------------"
    puts "Reset CONFREG to 0"
    puts "--------------------------"
    reset
    # remove polling, prevent openocd from complaining while reset tap
    poll off
    irscan gap8.cpu 0x7
    drscan gap8.cpu 0x4 0x0
    # set reset signals (direct control) jtag_reset 0 1
    jtag_reset 0 0
    # exit openocd, card will boot from flash
    exit
}

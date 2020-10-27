CC := clang
CREMOVE_UNUSED := -fdata-sections -ffunction-sections
CFLAGS += -O0 -Os -std=c11 -W -Wall -Wextra -pedantic -DPRINT_STATE_AT_EXIT # $(CREMOVE_UNUSED)
LDREMOVE_UNUSED := -Wl,--gc-sections
LDFLAGS += $(LDREMOVE_UNUSED)

TARGET := wm

SRC := $(wildcard *.c)
OBJ := $(SRC:%.c=.obj/%.o)
DEP := $(SRC:%.c=.obj/%.d)

.PHONY: clean all default

all: $(TARGET)
clean:
	$(RM) $(TARGET)
	$(RM) -r .obj

# Dependencies tracking
$(foreach BIN,$(TARGET),$(eval $(BIN): $(OBJ)))

$(TARGET): $(OBJ)
	$(LINK.o) -o $@ $^

$(OBJ) $(DEP): | .obj
.obj:
	mkdir $@
.obj/%.o: %.c
	$(COMPILE.c) -MMD -MP -o $@ $<

-include $(DEP)

keys = self.wnd.keys
        speed = 2.0 * dt
        rot_speed = 45.0 * dt
        scale_speed = 0.5 * dt

        # Translations
        if self.wnd.is_key_pressed(keys.O): object.position[2] -= speed # Forward
        if self.wnd.is_key_pressed(keys.L): object.position[2] += speed # Back

        if self.wnd.is_key_pressed(keys.K): object.position[0] -= speed # Left
        if self.wnd.is_key_pressed(keys.SEMICOLON): object.position[0] += speed # Right

        if self.wnd.is_key_pressed(keys.I): object.position[1] += speed # Up
        if self.wnd.is_key_pressed(keys.P): object.position[1] -= speed # Down

        # Rotations
        if self.wnd.is_key_pressed(keys.R): object.rotation[0] += rot_speed # ',' Rotate about X axis
        if self.wnd.is_key_pressed(keys.T): object.rotation[0] -= rot_speed # '.' Rotate about X axis

        if self.wnd.is_key_pressed(keys.F): object.rotation[1] += rot_speed # ',' Rotate about Y axis
        if self.wnd.is_key_pressed(keys.G): object.rotation[1] -= rot_speed # '.' Rotate about Y axis

        if self.wnd.is_key_pressed(keys.V): object.rotation[2] += rot_speed # ',' Rotate about Y axis
        if self.wnd.is_key_pressed(keys.B): object.rotation[2] -= rot_speed # '.' Rotate about Y axis
